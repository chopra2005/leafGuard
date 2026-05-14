from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "plantvillage dataset"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODELS_DIR / "plant_disease_mobilenetv2.keras"
CLASS_NAMES_PATH = MODELS_DIR / "class_names.json"

# Always train on the original PlantVillage color images (not segmented/grayscale).
DATA_SUBDIR = "color"

# If True, apply the same OpenCV pipeline as the Flask app on each color image.
# If False, only TensorFlow resize + normalize (still uses original color images).
USE_OPENCV_PREPROCESSING = True

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42


def main() -> None:
    train_root = DATA_ROOT / DATA_SUBDIR
    if not train_root.exists():
        raise FileNotFoundError(f"Dataset folder not found: {train_root}")

    class_names = sorted([p.name for p in train_root.iterdir() if p.is_dir()])
    num_classes = len(class_names)
    CLASS_NAMES_PATH.write_text(json.dumps(class_names, indent=2), encoding="utf-8")

    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    filepaths: list[str] = []
    labels: list[int] = []
    for class_idx, class_name in enumerate(class_names):
        class_dir = train_root / class_name
        for ext in exts:
            for fp in class_dir.glob(ext):
                filepaths.append(str(fp))
                labels.append(class_idx)

    filepaths_np = np.array(filepaths)
    labels_np = np.array(labels)

    train_files, test_files, train_labels, test_labels = train_test_split(
        filepaths_np, labels_np, test_size=0.15, stratify=labels_np, random_state=SEED
    )
    train_files, val_files, train_labels, val_labels = train_test_split(
        train_files,
        train_labels,
        test_size=0.15 / (1.0 - 0.15),
        stratify=train_labels,
        random_state=SEED,
    )

    autotune = tf.data.AUTOTUNE

    if USE_OPENCV_PREPROCESSING:
        import cv2
        from src.preprocessing.pipeline import LeafPreprocessor

        preprocessor = LeafPreprocessor()

        def cv2_preprocess_rgb(img_rgb_uint8: np.ndarray) -> np.ndarray:
            img_bgr = cv2.cvtColor(img_rgb_uint8, cv2.COLOR_RGB2BGR)
            out_rgb_uint8 = preprocessor.preprocess(img_bgr)
            return out_rgb_uint8.astype(np.float32) / 255.0

        def load_and_preprocess(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
            img_bytes = tf.io.read_file(path)
            img = tf.image.decode_image(img_bytes, channels=3, expand_animations=False)
            img = tf.cast(img, tf.uint8)
            out = tf.numpy_function(cv2_preprocess_rgb, [img], tf.float32)
            out.set_shape((IMG_SIZE[1], IMG_SIZE[0], 3))
            return out, tf.cast(label, tf.int32)

    else:

        def load_and_preprocess(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
            img_bytes = tf.io.read_file(path)
            img = tf.image.decode_image(img_bytes, channels=3, expand_animations=False)
            img = tf.image.resize(img, IMG_SIZE)
            img = tf.image.convert_image_dtype(img, tf.float32)
            return img, tf.cast(label, tf.int32)

    aug = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.12),
            tf.keras.layers.RandomZoom(0.12),
        ]
    )

    def make_ds(files: np.ndarray, lbls: np.ndarray, training: bool) -> tf.data.Dataset:
        ds = tf.data.Dataset.from_tensor_slices((files, lbls))
        if training:
            ds = ds.shuffle(buffer_size=min(len(files), 2000), seed=SEED, reshuffle_each_iteration=True)
        ds = ds.map(load_and_preprocess, num_parallel_calls=autotune)
        if training:
            ds = ds.map(lambda x, y: (aug(x, training=True), y), num_parallel_calls=autotune)
        return ds.batch(BATCH_SIZE).prefetch(autotune)

    ds_train = make_ds(train_files, train_labels, training=True)
    ds_val = make_ds(val_files, val_labels, training=False)
    ds_test = make_ds(test_files, test_labels, training=False)

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    x = base_model(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_accuracy", factor=0.5, patience=2),
    ]

    model.fit(ds_train, validation_data=ds_val, epochs=8, callbacks=callbacks)

    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )
    model.fit(ds_train, validation_data=ds_val, epochs=6, callbacks=callbacks)

    test_loss, test_acc = model.evaluate(ds_test)
    print(f"Test accuracy: {test_acc * 100:.2f}%")

    model.save(MODEL_PATH)
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved classes: {CLASS_NAMES_PATH}")


if __name__ == "__main__":
    main()
