import torch
import torch.nn as nn
from torchvision.transforms import transforms
from torchvision.models import vit_b_16
import os

# Định nghĩa các lớp cảm xúc
EMOTIONS = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']

# Định nghĩa transform cho ảnh đầu vào
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_vit_model(model_path):
    try:
        print(f"Loading model from: {model_path}")
        print(f"File exists: {os.path.exists(model_path)}")
        
        # Tạo mô hình ViT-B/16 với số lớp phân loại bằng số cảm xúc
        model = vit_b_16()
        # Thay đổi lớp head để phù hợp với số lớp cảm xúc
        model.heads = nn.Linear(model.hidden_dim, len(EMOTIONS))
        
        # Tải state dict với weights_only=True để tránh warning
        state_dict = torch.load(model_path, map_location=torch.device('cpu'), weights_only=True)
        print(f"State dict keys: {state_dict.keys() if isinstance(state_dict, dict) else 'Not a dict'}")
        
        # Nếu state_dict được lưu dưới dạng OrderedDict, lấy state_dict từ nó
        if not isinstance(state_dict, dict):
            state_dict = state_dict.state_dict()
        
        model.load_state_dict(state_dict)
        model.eval()
        print("Model loaded successfully")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def predict_emotion(model, image):
    try:
        if model is None:
            raise ValueError("Model is not loaded properly")
            
        # Chuyển ảnh sang tensor
        image_tensor = transform(image)
        image_tensor = image_tensor.unsqueeze(0)  # Thêm batch dimension
        
        # Dự đoán
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            predicted_idx = torch.argmax(probabilities).item()
            confidence = probabilities[0][predicted_idx].item()
            
        return EMOTIONS[predicted_idx], confidence
    except Exception as e:
        print(f"Error predicting emotion: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None, None 