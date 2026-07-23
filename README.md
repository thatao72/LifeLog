# LifeLog

Garmin Connectからライフログ関連データを取得・整理するためのスクリプト群。

## ランニングHRゾーンしきい値の変更履歴

`running_hr_zone_changes.py` は、指定期間内のランニングアクティビティを取得し、各アクティビティに保存されたHRゾーン1〜5の下限値を比較する。

直前のランニング実施日と比べて、しきい値が変わった日のみCSVへ出力する。比較対象となる最初のランニング日は出力しない。同日に複数のランニングがある場合は、その日の最後のアクティビティを採用する。

### 1. セットアップ

Python仮想環境を作成し、依存ライブラリをインストールする。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Garmin認証情報

認証情報を `.env` に保存している場合、zshでは次のように読み込む。

`.env` に `export` が付いている場合：

```bash
source .env
```

`.env` に `export` が付いていない場合：

```bash
set -a
source .env
set +a
```

必要な環境変数：

```bash
GARMIN_USERNAME='Garmin Connectのメールアドレス'
GARMIN_PASSWORD='Garmin Connectのパスワード'
GARMIN_TOKEN_DIR="$HOME/.garminconnect"
```

環境変数が読み込まれたか確認する。

```bash
env | grep '^GARMIN_'
```

`.env` とGarmin認証トークンはGitへコミットしないこと。

### 3. 単体テスト

Garmin Connectへ接続せず、HRゾーンの解析、ランニング判定、変更日の抽出、CSV出力を確認する。

```bash
python -m unittest discover -s tests -v
```

### 4. 短期間で実データ確認

まず短い期間で取得結果を確認する。

```bash
python running_hr_zone_changes.py \
  --start-date 2026-06-01 \
  --end-date 2026-07-22 \
  --output ./running_hr_zone_changes.csv \
  --raw-json ./running_hr_zone_snapshots.json
```

- `running_hr_zone_changes.csv`: しきい値が変わった日だけを出力
- `running_hr_zone_snapshots.json`: 取得できた全ランニングのしきい値スナップショット

期間内に変更がなければ、CSVはヘッダーだけになる。

### 5. 2022年5月2日以降の全期間を取得

`--end-date` を省略すると実行日までを取得する。

```bash
python running_hr_zone_changes.py \
  --start-date 2022-05-02 \
  --output ./running_hr_zone_changes.csv \
  --raw-json ./running_hr_zone_snapshots.json
```

### 6. CSV出力形式

```text
date,activity_id,activity_name,zone1_min,zone2_min,zone3_min,zone4_min,zone5_min
```

各 `zoneN_min` は、そのゾーンの下限心拍数（bpm）。

### 7. エラー調査

通常モードでは、利用可能なHRゾーンデータがないアクティビティをスキップする。最初の取得エラーで停止して原因を確認する場合は `--strict` を付ける。

```bash
python running_hr_zone_changes.py \
  --start-date 2026-06-01 \
  --end-date 2026-07-22 \
  --output ./running_hr_zone_changes.csv \
  --raw-json ./running_hr_zone_snapshots.json \
  --strict
```
