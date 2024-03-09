import torch
from torch.utils.data import DataLoader
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_fpn
from torchvision.models.detection.faster_rcnn import FasterRCNN_MobileNet_V3_Large_FPN_Weights
from torchvision.datasets import CocoDetection
import torchvision.transforms as T
from torch.utils.tensorboard import SummaryWriter
from torch.optim.lr_scheduler import ReduceLROnPlateau
import matplotlib.pyplot as plt
import numpy as np

# Assuming utils.py contains the calculate_iou function and possibly more in the future
from utils import calculate_iou, collate_fn 

# Device configuration
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

# Load the pre-trained model
model = fasterrcnn_mobilenet_v3_large_fpn(weights=FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT).to(device)

# Freeze the backbone parameters
for param in model.backbone.parameters():
    param.requires_grad = False

# Define transformations
transform = T.Compose([
    T.Resize((640, 512)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load datasets
train_data = CocoDetection(root='./FLIR_ADAS_v2/images_thermal_train', 
                           annFile='./FLIR_ADAS_v2/images_thermal_train/coco.json', transform=transform)
val_data = CocoDetection(root='./FLIR_ADAS_v2/images_thermal_val', 
                         annFile='./FLIR_ADAS_v2/images_thermal_val/coco.json', transform=transform)
test_data = CocoDetection(root='./FLIR_ADAS_v2/video_thermal_test', 
                          annFile='./FLIR_ADAS_v2/video_thermal_test/coco.json', transform=transform)

# Data loaders
train_loader = DataLoader(train_data, batch_size=4, shuffle=True, num_workers=4, collate_fn=collate_fn)
val_loader = DataLoader(val_data, batch_size=4, shuffle=False, num_workers=4, collate_fn=collate_fn)
test_loader = DataLoader(test_data, batch_size=4, shuffle=False, num_workers=4, collate_fn=collate_fn)

# Optimizer
optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005)

# Loss criterion is not directly used since loss is computed within model
# Scheduler
scheduler = ReduceLROnPlateau(optimizer, 'min')

# SummaryWriter for TensorBoard
writer = SummaryWriter()

# Training settings
epochs = 100
best_val_loss = float('inf')
epochs_no_improve = 0
n_epochs_stop = 10

print('Start Training')

# Main training loop
for epoch in range(epochs):
    model.train()
    running_loss = 0.0

    for images, targets in train_loader:
        images = [image.to(device) for image in images]
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

        running_loss += losses.item()

    train_loss = running_loss / len(train_loader)
    writer.add_scalar('Loss/train', train_loss, epoch)
    print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {train_loss:.4f}')

    # Validation step omitted for brevity

writer.close()
print('Finished Training')

# Optional: Add prediction visualization or evaluation here
import torchvision.transforms.functional as F

def visualize_predictions(image, targets, threshold=0.5):
    """Visualizes predictions on the image with bounding boxes."""
    image = F.to_pil_image(image)
    draw = ImageDraw.Draw(image)
    for target in targets:
        box = target['boxes'].cpu().numpy()
        score = target['scores'].cpu().numpy()
        if score > threshold:
            draw.rectangle(((box[0], box[1]), (box[2], box[3])), outline="red")
    display(image)

# Pick a few images from the test dataset
model.eval()
with torch.no_grad():
    for images, _ in test_loader:
        images = [image.to(device) for image in images]
        outputs = model(images)
        
        # Visualize predictions for the first image in the batch
        visualize_predictions(images[0].cpu(), outputs[0])
        break  # Visualize predictions for one image at a time
