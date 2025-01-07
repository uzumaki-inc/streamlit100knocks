## setup

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

## ログインアカウント生成

.env
python common/gen_account.py
