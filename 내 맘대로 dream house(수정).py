import os
import requests
from flask import Flask, render_template, request, redirect, url_for
import ezdxf
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 사진 파일 업로드 경로 설정
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Option:
    def __init__(self, name, price, company):
        self.name = name
        self.price = price
        self.company = company

class Furniture:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class HouseDesignProgram:
    def __init__(self):
        self.api_key = 'AIzaSyD5_JdX_a7qntiupmcNxSu6Vb0h*******'  # 구글 API 키 추가
        self.furnitures = [
            Furniture("소파", 300),
            Furniture("테이블", 150),
            Furniture("의자", 100),
        ]
        self.wall_interior_options = [
            Option("내부 페인트", 50, "업체 A"),
            Option("벽지", 30, "업체 B"),
        ]
        self.wall_exterior_options = [
            Option("외부 페인트", 70, "업체 C"),
            Option("타일", 90, "업체 D"),
        ]
        self.electrical_options = [
            Option("냉장고", 500, "업체 E"),
            Option("세탁기", 400, "업체 F"),
            Option("에어컨", 600, "업체 G"),
        ]
        self.kitchen_options = [
            Option("싱크대", 250, "업체 H"),
            Option("조리용 전열기", 200, "업체 I"),
        ]
        self.garden_options = ["정원", "풀밭", "꽃밭", "바베큐 공간", "벤치"]
    
    def get_land_info(self, address):
        """도로명 주소를 사용하여 위치 정보를 가져옵니다."""
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&language=ko&key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return data['results'][0]['geometry']['location']
        return None

    def create_cad_drawing(self, filename, width, height, image_path):
        """CAD 도면을 생성합니다."""
        doc = ezdxf.new()
        msp = doc.modelspace()
        msp.add_line(start=(0, 0), end=(width, 0))
        msp.add_line(start=(width, 0), end=(width, height))
        msp.add_line(start=(width, height), end=(0, height))
        msp.add_line(start=(0, height), end=(0, 0))

        # 이미지 추가 (주석으로 추가된 예시로 실제 CAD에 이미지를 삽입하는 방법은 다를 수 있음)
        # msp.add_image(image_path, insert=(width / 2, height / 2), size=(100, 100))

        doc.saveas(filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        address = request.form['address']
        width = float(request.form['width'])
        height = float(request.form['height'])
        floors = int(request.form['floors'])

        # 이미지 파일 처리
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            program = HouseDesignProgram()
            land_info = program.get_land_info(address)
            
            if land_info:
                total_height = floors * height
                program.create_cad_drawing("house_plan.dxf", width, total_height, image_path)
                return render_template('result.html', land_info=land_info, width=width, total_height=total_height)

    return render_template('index.html')

@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'POST':
        # 사용자가 선택한 옵션 처리
        pass
    return render_template('options.html', furnitures=HouseDesignProgram().furnitures)

if __name__ == '__main__':
    # uploads 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)
