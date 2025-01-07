from setuptools import setup, find_packages

setup(
    name="knocks",  # プロジェクト名
    version="0.1",
    packages=find_packages(),  # commonやknocksなどを自動的に含む
    install_requires=["python-dotenv"],  # 必要な依存関係を記述
)
