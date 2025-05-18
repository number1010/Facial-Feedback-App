# Facial Feedback App

Ứng dụng phân tích cảm xúc người dùng thông qua webcam và gửi phản hồi cho nhà nghiên cứu thị trường.

## Tính năng chính

- Đăng ký/đăng nhập người dùng
- Phân tích cảm xúc qua webcam
- Gửi phản hồi về sản phẩm
- Dashboard cho nhà nghiên cứu thị trường
- Quản lý sản phẩm và chủ đề

## Cài đặt

1. Clone repository:
```bash
git clone [repository-url]
cd facial_feedback_app
```

2. Tạo môi trường ảo và cài đặt dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Chạy migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Tạo superuser:
```bash
python manage.py createsuperuser
```

5. Chạy server:
```bash
python manage.py runserver
```

## Công nghệ sử dụng

- Python 3.x
- Django 5.2
- OpenCV
- DeepFace
- Bootstrap 5
- SQLite3

## Cấu trúc project

- `accounts/`: Quản lý người dùng và sản phẩm
- `emotion_feedback/`: Xử lý phân tích cảm xúc và phản hồi
- `templates/`: Giao diện người dùng
- `static/`: CSS, JavaScript và media files

## SCRUM Process

This project is managed using SCRUM methodology:
- Sprint duration: 2 weeks
- Daily standups
- Sprint planning and retrospective meetings
- Project board maintained on GitHub Projects

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 