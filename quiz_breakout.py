"""
AWS Quiz Breakout
ブロック崩しゲームとAWSサービスクイズを組み合わせたゲーム

使用方法:
python quiz_breakout.py

必要なライブラリ:
- pygame
- (オプション) cairosvg (SVGファイルを使用する場合)

詳細はREADME.mdを参照してください。
"""

import pygame
import sys
import random
import os
import io

# SVGサポートの確認
SVG_SUPPORT = False
try:
    import cairosvg
    SVG_SUPPORT = True
except ImportError:
    print("cairosvgのインポートに失敗しました。PNGファイルを使用します。")

# SVGファイルを読み込む関数
def load_svg(filename, width, height):
    if not SVG_SUPPORT:
        # SVGサポートがない場合はプレースホルダーを返す
        surface = pygame.Surface((width, height))
        surface.fill((173, 216, 230))  # 水色の背景
        
        # ファイル名からサービス名を抽出
        service_name = filename.split('/')[-1].split('.')[0].upper()
        text = font.render(service_name, True, (0, 0, 0))
        surface.blit(text, (width//2 - text.get_width()//2, height//2 - text.get_height()//2))
        return surface
    
    try:
        # SVGをPNGに変換
        png_data = cairosvg.svg2png(url=filename, output_width=width, output_height=height)
        
        # PNGデータからPygame用のSurfaceを作成
        png_file = io.BytesIO(png_data)
        return pygame.image.load(png_file)
    except Exception as e:
        print(f"SVG読み込みエラー: {e}")
        # エラーの場合はプレースホルダーを返す
        surface = pygame.Surface((width, height))
        surface.fill((173, 216, 230))  # 水色の背景
        return surface

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AWS Quiz Breakout")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
COLORS = [RED, GREEN, BLUE, ORANGE]

# フォント設定
try:
    # macOSの日本語フォント
    font = pygame.font.Font('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 24)
    large_font = pygame.font.Font('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 36)
except:
    try:
        # Windowsの日本語フォント
        font = pygame.font.Font('C:/Windows/Fonts/meiryo.ttc', 24)
        large_font = pygame.font.Font('C:/Windows/Fonts/meiryo.ttc', 36)
    except:
        # フォントが見つからない場合はデフォルトフォント
        print("日本語フォントが見つかりません。文字化けする可能性があります。")
        font = pygame.font.SysFont(None, 36)
        large_font = pygame.font.SysFont(None, 48)

# パドル設定
paddle_width = 100
paddle_height = 20
paddle_x = WIDTH // 2 - paddle_width // 2
paddle_y = HEIGHT - 50
paddle_speed = 8

# ボール設定
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 3  # 速度を遅く
ball_dy = -3  # 速度を遅く
ball_color = (255, 165, 0)  # オレンジ色のボール

# ブロック設定
# 画像エリアの設定
image_size = min(WIDTH - 100, HEIGHT // 2)  # 正方形のエリア
image_width = image_size
image_height = image_size
image_x = (WIDTH - image_width) // 2  # 中央に配置
image_y = 50

# ブロックサイズを画像に合わせて計算（正方形）
block_cols = 6
block_rows = 6
block_size = image_size // block_cols  # 正方形のブロック
block_width = block_size
block_height = block_size
blocks = []

# AWSサービスクイズ設定
quiz_images = [
    {"path": "images/s3.png", "question": "このAWSサービスは何ですか？", "answer": "Amazon S3", 
     "options": ["Amazon S3", "Amazon EC2", "AWS Lambda"]},
    {"path": "images/ec2.png", "question": "このAWSサービスは何ですか？", "answer": "Amazon EC2", 
     "options": ["Amazon RDS", "Amazon EC2", "Amazon DynamoDB"]},
    {"path": "images/lambda.png", "question": "このAWSサービスは何ですか？", "answer": "AWS Lambda", 
     "options": ["AWS Lambda", "Amazon SQS", "Amazon SNS"]},
    {"path": "images/dynamodb.png", "question": "このAWSサービスは何ですか？", "answer": "Amazon DynamoDB", 
     "options": ["Amazon Aurora", "Amazon DynamoDB", "Amazon RDS"]},
    {"path": "images/cloudfront.png", "question": "このAWSサービスは何ですか？", "answer": "Amazon CloudFront", 
     "options": ["Amazon Route 53", "Amazon CloudFront", "Amazon API Gateway"]}
]

# SVGファイルが利用可能な場合は拡張子を変更
if SVG_SUPPORT:
    for quiz in quiz_images:
        quiz["path"] = quiz["path"].replace(".png", ".svg")

# 現在のクイズインデックス
current_quiz_index = 0
background_image = None

# ゲームの状態
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_QUIZ = 2
STATE_RESULT = 3
STATE_GAMEOVER = 4
game_state = STATE_TITLE
current_quiz = None
revealed_image = None
quiz_result = False


# ゲームのリセット
def reset_game():
    global paddle_x, paddle_y, ball_x, ball_y, ball_dx, ball_dy, current_quiz_index
    
    paddle_x = WIDTH // 2 - paddle_width // 2
    paddle_y = HEIGHT - 50
    ball_x = WIDTH // 2
    ball_y = paddle_y - ball_radius - 5  # パドルの上にボールを配置
    ball_dx = 3  # 速度を遅く
    ball_dy = -3  # 速度を遅く
    
    # 新しいクイズを選択
    current_quiz_index = random.randint(0, len(quiz_images) - 1)
    init_blocks()

# ブロックの初期化
def init_blocks():
    global blocks, current_quiz_index, background_image
    blocks = []
    
    # ランダムにクイズを選択
    current_quiz_index = random.randint(0, len(quiz_images) - 1)
    
    # 背景画像の作成（プレースホルダー）
    background_image = pygame.Surface((image_width, image_height))
    background_image.fill((173, 216, 230))  # 水色の背景
    
    # 実際のゲームでは画像をロード
    try:
        path = quiz_images[current_quiz_index]["path"]
        if path.lower().endswith('.svg'):
            bg_img = load_svg(path, image_width, image_height)
        else:
            try:
                bg_img = pygame.image.load(path)
            except:
                # 画像が見つからない場合はプレースホルダーを作成
                bg_img = pygame.Surface((image_width, image_height))
                bg_img.fill((173, 216, 230))  # 水色の背景
                service_name = quiz_images[current_quiz_index]["answer"]
                text = large_font.render(service_name, True, BLACK)
                bg_img.blit(text, (bg_img.get_width()//2 - text.get_width()//2, 
                                  bg_img.get_height()//2 - text.get_height()//2))
        
        # アスペクト比を保持してリサイズ
        img_width, img_height = bg_img.get_size()
        ratio = min(image_width / img_width, image_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        resized_img = pygame.transform.scale(bg_img, (new_width, new_height))
        
        # 中央に配置
        background_image = pygame.Surface((image_width, image_height))
        background_image.fill((173, 216, 230))  # 水色の背景
        x_offset = (image_width - new_width) // 2
        y_offset = (image_height - new_height) // 2
        background_image.blit(resized_img, (x_offset, y_offset))
    except:
        # 画像が見つからない場合はプレースホルダーテキスト
        text = large_font.render("AWS " + quiz_images[current_quiz_index]["answer"], True, BLACK)
        background_image.blit(text, (background_image.get_width()//2 - text.get_width()//2, 
                                    background_image.get_height()//2 - text.get_height()//2))
    
    # ブロックの配置（画像エリアに合わせて整列）
    for row in range(block_rows):
        for col in range(block_cols):
            x = col * block_width + image_x
            y = row * block_height + image_y
            
            blocks.append({
                "rect": pygame.Rect(x, y, block_width, block_height),
                "color": random.choice(COLORS),
                "visible": True
            })

# クイズの表示
def show_quiz():
    global game_state, current_quiz
    
    game_state = STATE_QUIZ
    current_quiz = quiz_images[current_quiz_index]

# クイズの描画
def draw_quiz():
    # 背景
    screen.fill(BLACK)
    
    # 質問テキスト
    question_text = font.render(current_quiz["question"], True, WHITE)
    screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 150))
    
    # 選択肢のサイズを計算
    max_width = 0
    for option in current_quiz["options"]:
        option_text = font.render(option, True, WHITE)
        max_width = max(max_width, option_text.get_width())
    
    button_width = max_width + 60  # テキストの幅 + 余白
    
    # 選択肢
    for i, option in enumerate(current_quiz["options"]):
        option_rect = pygame.Rect(WIDTH//2 - button_width//2, 250 + i*70, button_width, 50)
        pygame.draw.rect(screen, BLUE, option_rect)
        
        option_text = font.render(option, True, WHITE)
        screen.blit(option_text, (option_rect.centerx - option_text.get_width()//2, 
                                 option_rect.centery - option_text.get_height()//2))

# 結果画面の描画
def draw_result():
    screen.fill(BLACK)
    
    if quiz_result:
        result_text = large_font.render("Congratulations!", True, GREEN)
    else:
        result_text = large_font.render("残念！", True, RED)
    
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 100))
    
    # 再プレイボタン
    replay_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 50)
    pygame.draw.rect(screen, BLUE, replay_rect)
    replay_text = font.render("もう一度プレイする", True, WHITE)
    screen.blit(replay_text, (replay_rect.centerx - replay_text.get_width()//2, 
                             replay_rect.centery - replay_text.get_height()//2))
    
    # 終了ボタン
    exit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 70, 300, 50)
    pygame.draw.rect(screen, RED, exit_rect)
    exit_text = font.render("ゲームを終了する", True, WHITE)
    screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width()//2, 
                           exit_rect.centery - exit_text.get_height()//2))

# タイトル画面の描画
def draw_title():
    screen.fill(BLACK)
    
    # タイトルテキスト
    title_text = large_font.render("AWS Quiz Breakout", True, ORANGE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
    
    # サブタイトル
    subtitle_text = font.render("ブロック崩しでAWSサービスを学ぼう", True, WHITE)
    screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 150))
    
    # 遊び方の説明
    instruction_text1 = font.render("ブロックを崩して隠れたAWSサービスを当てよう！", True, WHITE)
    instruction_text2 = font.render("左右キーでパドルを操作", True, WHITE)
    instruction_text3 = font.render("ブロックの背後に隠された画像を見て何のサービスか答えよう", True, WHITE)
    screen.blit(instruction_text1, (WIDTH//2 - instruction_text1.get_width()//2, 200))
    screen.blit(instruction_text2, (WIDTH//2 - instruction_text2.get_width()//2, 240))
    screen.blit(instruction_text3, (WIDTH//2 - instruction_text3.get_width()//2, 280))
    
    # スタートボタン
    start_rect = pygame.Rect(WIDTH//2 - 150, 350, 300, 50)
    pygame.draw.rect(screen, BLUE, start_rect)
    start_text = font.render("ゲームスタート", True, WHITE)
    screen.blit(start_text, (start_rect.centerx - start_text.get_width()//2, 
                            start_rect.centery - start_text.get_height()//2))
    
    # 終了ボタン
    exit_rect = pygame.Rect(WIDTH//2 - 150, 420, 300, 50)
    pygame.draw.rect(screen, RED, exit_rect)
    exit_text = font.render("ゲームを終了する", True, WHITE)
    screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width()//2, 
                           exit_rect.centery - exit_text.get_height()//2))

# ゲーム初期化
init_blocks()

# ゲームループ
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # タイトル画面のマウスクリック処理
        if game_state == STATE_TITLE and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            start_rect = pygame.Rect(WIDTH//2 - 150, 350, 300, 50)
            exit_rect = pygame.Rect(WIDTH//2 - 150, 420, 300, 50)
            
            if start_rect.collidepoint(mouse_pos):
                game_state = STATE_PLAYING
                reset_game()
            elif exit_rect.collidepoint(mouse_pos):
                running = False
        
        # クイズ中のマウスクリック処理
        if game_state == STATE_QUIZ and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 選択肢のサイズを計算
            max_width = 0
            for option in current_quiz["options"]:
                option_text = font.render(option, True, WHITE)
                max_width = max(max_width, option_text.get_width())
            
            button_width = max_width + 60  # テキストの幅 + 余白
            
            for i, option in enumerate(current_quiz["options"]):
                option_rect = pygame.Rect(WIDTH//2 - button_width//2, 250 + i*70, button_width, 50)
                if option_rect.collidepoint(mouse_pos):
                    # 正解判定
                    quiz_result = (option == current_quiz["answer"])
                    
                    game_state = STATE_RESULT
        
        # 結果画面のマウスクリック処理
        elif game_state == STATE_RESULT and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 再プレイボタン
            replay_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 50)
            if replay_rect.collidepoint(mouse_pos):
                reset_game()
                game_state = STATE_PLAYING
            
            # 終了ボタン
            exit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 70, 300, 50)
            if exit_rect.collidepoint(mouse_pos):
                running = False
    
    # タイトル画面の描画
    if game_state == STATE_TITLE:
        draw_title()
    
    # ゲームプレイ中の処理
    elif game_state == STATE_PLAYING:
        # キー入力処理
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed
        
        # ボールの移動
        ball_x += ball_dx
        ball_y += ball_dy
        
        # 壁との衝突判定
        if ball_x <= ball_radius or ball_x >= WIDTH - ball_radius:
            ball_dx = -ball_dx
        if ball_y <= ball_radius:
            ball_dy = -ball_dy
        
        # パドルとの衝突判定
        if (ball_y + ball_radius >= paddle_y and ball_y <= paddle_y + paddle_height and
            ball_x >= paddle_x and ball_x <= paddle_x + paddle_width):
            ball_dy = -abs(ball_dy)  # 上向きに反射
            
            # パドルの位置によって反射角度を変える
            paddle_center = paddle_x + paddle_width / 2
            ball_offset = (ball_x - paddle_center) / (paddle_width / 2)
            ball_dx = ball_offset * 3  # 最大速度を調整
        
        # ブロックとの衝突判定
        collision_detected = False
        for block in blocks:
            if block["visible"] and block["rect"].colliderect(pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius*2, ball_radius*2)):
                # 衝突方向に基づいて反射（貫通しない）
                block_center_x = block["rect"].centerx
                block_center_y = block["rect"].centery
                
                # ボールの中心からブロックの中心へのベクトル
                dx = ball_x - block_center_x
                dy = ball_y - block_center_y
                
                # x方向とy方向のどちらから衝突したかを判定
                if abs(dx) * block_height > abs(dy) * block_width:
                    # x方向からの衝突
                    ball_dx = -ball_dx
                else:
                    # y方向からの衝突
                    ball_dy = -ball_dy
                
                block["visible"] = False
                collision_detected = True
                
                # すべてのブロックが消えたか確認
                if not any(block["visible"] for block in blocks):
                    # すべて消えた場合、クイズを表示
                    show_quiz()
                
                # 一つのブロックとの衝突で処理を終了（貫通防止）
                break
        
        # ボールが落ちた場合
        if ball_y >= HEIGHT:
            # ボールを落とした場合もクイズを表示
            visible_blocks = [b for b in blocks if b["visible"]]
            if visible_blocks:
                show_quiz()
            else:
                # すべてのブロックが消えている場合はゲーム終了
                game_state = STATE_GAMEOVER
        
        # 描画処理
        screen.fill(BLACK)
        
        # 背景画像の描画（ブロックの背後に1枚の大きな画像）
        bg_area = pygame.Rect(image_x, image_y, image_width, image_height)
        screen.blit(background_image, bg_area)
        
        # ブロックの描画
        for block in blocks:
            if block["visible"]:
                pygame.draw.rect(screen, block["color"], block["rect"])
        
        # パドルの描画
        pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))
        
        # ボールの描画（最後に描画して最前面に表示）
        pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), ball_radius)

    
    # クイズ中の描画
    elif game_state == STATE_QUIZ:
        draw_quiz()
    
    # 結果画面の描画
    elif game_state == STATE_RESULT:
        draw_result()
    
    # ゲームオーバー画面
    elif game_state == STATE_GAMEOVER:
        screen.fill(BLACK)
        game_over_text = large_font.render("ゲームオーバー", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        
        # 再プレイボタン
        replay_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 50)
        pygame.draw.rect(screen, BLUE, replay_rect)
        replay_text = font.render("もう一度プレイする", True, WHITE)
        screen.blit(replay_text, (replay_rect.centerx - replay_text.get_width()//2, 
                                 replay_rect.centery - replay_text.get_height()//2))
        
        # 終了ボタン
        exit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 90, 300, 50)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = font.render("ゲームを終了する", True, WHITE)
        screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width()//2, 
                               exit_rect.centery - exit_text.get_height()//2))
        
        # マウスクリック処理
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if replay_rect.collidepoint(mouse_pos):
                reset_game()
                game_state = STATE_PLAYING
            elif exit_rect.collidepoint(mouse_pos):
                running = False
    
    # 画面更新
    pygame.display.flip()
    clock.tick(60)  # 60FPS

# 終了処理
pygame.quit()
sys.exit()