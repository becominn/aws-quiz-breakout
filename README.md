# AWS Quiz Breakout

ブロック崩しゲームとAWSサービスクイズを組み合わせたゲームです。ブロックの後ろに隠されたAWSサービスアイコンを当てるクイズに挑戦しましょう。

## 遊び方

1. 左右の矢印キーでパドルを操作し、ボールでブロックを崩します
2. ブロックをすべて崩すか、ボールを落とすとクイズが表示されます
3. 表示されたAWSサービスアイコンが何かを当てましょう
4. 正解すると「Congratulations!」、不正解なら「残念！」と表示されます
5. クイズの後は「もう一度プレイする」か「ゲームを終了する」を選べます

## 必要なもの

- Python 3.x
- Pygame
- (オプション) cairosvg - SVGファイルを使用する場合

## インストール方法

### 基本インストール
```bash
pip install pygame
```

### SVGサポートを有効にする場合（オプション）
SVGファイルを使用する場合は、以下のライブラリも必要です：

#### macOS
```bash
brew install cairo
pip install cairosvg
```

#### Windows
```bash
pip install cairosvg
```
※ Windowsの場合、GTK+のインストールが必要な場合があります。

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install libcairo2-dev
pip install cairosvg
```

## 実行方法

```bash
python quiz_breakout.py
```

## 画像の準備

ゲームを実行するには、AWSサービスアイコンの画像が必要です。以下のいずれかの方法で準備してください：

1. AWS公式サイトからアイコンをダウンロードし、`images`フォルダに配置
2. 独自のアイコンを作成し、`images`フォルダに配置
3. 画像がない場合は、自動的にプレースホルダーが表示されます

必要な画像ファイル名：
- s3.png (または s3.svg)
- ec2.png (または ec2.svg)
- lambda.png (または lambda.svg)
- dynamodb.png (または dynamodb.svg)
- cloudfront.png (または cloudfront.svg)

## カスタマイズ

`quiz_breakout.py` の `quiz_images` リストを編集することで、クイズを追加・変更できます。

例:
```python
quiz_images = [
    {"path": "images/s3.png", "question": "このAWSサービスは何ですか？", "answer": "Amazon S3", 
     "options": ["Amazon S3", "Amazon EC2", "AWS Lambda"]},
    # 他のクイズを追加
]
```

## ライセンス

このゲームは自由に使用・改変・再配布できます。ただし、AWSサービスアイコンを使用する場合は、AWSの利用規約に従ってください。