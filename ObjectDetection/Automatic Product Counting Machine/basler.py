from pypylon import pylon
import cv2  # OpenCV
import os
from datetime import datetime  # Để lấy thời gian hiện tại

# Tạo trình điều khiển camera
tl_factory = pylon.TlFactory.GetInstance()

# Tìm kiếm camera qua giao thức GigE
#camera = tl_factory.CreateFirstDevice()

# Hoặc nếu bạn đã biết IP của camera, sử dụng cụ thể địa chỉ IP
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(pylon.DeviceInfo().SetIpAddress("192.168.3.3")))

# Mở camera
camera.Open()

# Cài đặt kích thước ảnh Full HD (1920x1080)
#camera.Width.SetValue(1920)
#camera.Height.SetValue(1080)
max_width = camera.Width.GetMax()  # Lấy giá trị tối đa cho chiều rộng
max_height = camera.Height.GetMax()  # Lấy giá trị tối đa cho chiều cao

# Đặt kích thước ảnh về tối đa
camera.Width.SetValue(max_width)
camera.Height.SetValue(max_height)

# Điều chỉnh Gain (độ nhạy cảm biến) và thời gian phơi sáng
camera.Gain.SetValue(10)  # Đặt giá trị Gain (tăng giảm độ sáng). Bạn có thể thay đổi giá trị này.
camera.ExposureTime.SetValue(5000)  # Đặt thời gian phơi sáng (5000 micro giây = 5ms)

# Chụp hình ảnh
grab_result = camera.GrabOne(1000)

# Kiểm tra nếu hình ảnh đã được chụp thành công
if grab_result.GrabSucceeded():
    # Lưu hình ảnh hoặc xử lý tùy thích
    image = grab_result.Array
    
    print("Image captured successfully.")
    
     # Thu nhỏ hình ảnh xuống 25% kích thước gốc
    scale_percent = 25  # 25% của kích thước ban đầu
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)

    # Thay đổi kích thước hình ảnh
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    # Hiển thị hình ảnh đã thu nhỏ bằng OpenCV
    cv2.imshow('Captured Image (Resized to 25%)', resized_image)
    # Đợi phím bấm bất kỳ để đóng cửa sổ hình ảnh
    cv2.waitKey(0)
    # Lấy thời gian hiện tại và tạo tên file theo giờ-phút ngày-tháng
    current_time = datetime.now().strftime("%H-%M_%d-%m")
    output_filename = f"captured_image_{current_time}.png"

    # Tạo đường dẫn để lưu hình ảnh
    output_path = os.path.join(os.getcwd(), output_filename)
    
    # Lưu hình ảnh xuống thư mục hiện tại
    cv2.imwrite(output_path, image)
    print(f"Image saved as {output_path}")
    
else:
    print("Failed to capture image.")

# Đóng camera sau khi sử dụng
camera.Close()

cv2.destroyAllWindows()