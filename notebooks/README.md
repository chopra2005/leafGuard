# Notebook Plan (Weeks 4-5)

Create a Jupyter notebook named `plant_disease_mobilenetv2.ipynb` (added to this repo) and follow this sequence:

1. Load PlantVillage images from `plantvillage dataset/color` (original images; not segmented/grayscale).
2. Split into train/validation/test.
3. Apply preprocessing pipeline used by the app (resize to 224x224, normalize to [0, 1]).
4. Load `MobileNetV2` with `include_top=False`, `weights='imagenet'`.
5. Add custom dense head for class prediction.
6. Train initial head with base model frozen.
7. Fine-tune selected upper layers with low learning rate.
8. Evaluate and save model to:
   - `models/plant_disease_mobilenetv2.keras`
9. Export class names in the same index order used during training.
