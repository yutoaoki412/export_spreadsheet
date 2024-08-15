# BigQuery から Google Sheets へのエクスポート

このプロジェクトは、Google Cloud Functions (第2世代) を使用して BigQuery から Google Sheets にデータをエクスポートするプロセスを自動化します。Cloud Scheduler と Pub/Sub を利用して、日次、週次、月次のエクスポートをスケジュールします。

## 目次

1. [前提条件](#前提条件)
2. [プロジェクト構造](#プロジェクト構造)
3. [セットアップ](#セットアップ)
4. [デプロイ](#デプロイ)
   - [プロジェクトの設定](#プロジェクトの設定)
   - [サービスアカウントの設定](#サービスアカウントの設定)
   - [Pub/Sub トピックの作成](#pubsub-トピックの作成)
   - [Cloud Functions へのデプロイ](#cloud-functions-へのデプロイ)
   - [Cloud Scheduler の設定](#cloud-scheduler-の設定)
5. [設定](#設定)
6. [トラブルシューティング](#トラブルシューティング)

## 前提条件

- 課金が有効な Google Cloud Platform アカウント
- インストールおよび設定済みの `gcloud` CLI（最新版）
- Python 3.7 以降
- BigQuery、Google Sheets、Pub/Sub API へのアクセス権限

## プロジェクト構造

```
.
├── main.py
├── google_api_handler.py
├── utils.py
├── config.yml
├── requirements.txt
└── queries/
    ├── daily/
    ├── weekly/
    └── monthly/
```

## セットアップ

1. リポジトリをクローンします：
   ```
   git clone <リポジトリURL>
   cd <プロジェクトディレクトリ>
   ```

2. 仮想環境を作成してアクティベートします：
   ```
   python -m venv venv
   source venv/bin/activate
   
   # Windows の場合は `venv\Scripts\activate`
   ```

3. 必要なパッケージをインストールします：
   ```
   pip install -r requirements.txt
   ```

4. `config.yml` ファイルをプロジェクト ID とクエリの設定で更新します。

5. SQL クエリファイルを `queries/` 以下の適切なディレクトリに配置します。

## デプロイ

### プロジェクトの設定

1. プロジェクトを設定します：
   ```bash
   export GOOGLE_CLOUD_PROJECT=<あなたのプロジェクトID>
   ```

   または、以下のコマンドでプロジェクトを設定します：

   ```bash
   gcloud config set project <あなたのプロジェクトID>
   ```

2. 必要な API を有効にします：
   ```
   gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com pubsub.googleapis.com sheets.googleapis.com bigquery.googleapis.com
   ```

### サービスアカウントの設定

1. 新しいサービスアカウントを作成します：
   ```
   gcloud iam service-accounts create bq-sheets-exporter --display-name "BigQuery to Sheets Exporter"
   ```

2. 必要な権限を付与します：
   ```
   gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member="serviceAccount:bq-sheets-exporter@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
     --role="roles/bigquery.user"

   gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member="serviceAccount:bq-sheets-exporter@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
     --role="roles/sheets.editor"
   ```

3. サービスアカウントにGoogle Driveのファイルまたはフォルダへのアクセス権限を付与します：
   - Google Driveで対象のファイル（スプレッドシート）またはフォルダを右クリックし、「共有」を選択します。
   - 「ユーザーやグループを追加」フィールドに、作成したサービスアカウントのメールアドレス（bq-sheets-exporter@<プロジェクトID>.iam.gserviceaccount.com）を入力します。
   - 権限を「編集者」に設定します。
   - 「送信」をクリックして、権限を付与します。

   注意: 
   - フォルダに対して権限を付与する場合、そのフォルダ内の既存のファイルと今後作成されるファイルに権限が適用されます。
   - 個別のファイルに対して権限を付与する場合、`config.yml`ファイルで指定した各スプレッドシートに対してこの操作を行う必要があります。
   - 大量のスプレッドシートがある場合は、それらをまとめて1つのフォルダに配置し、そのフォルダに対して権限を付与することをお勧めします。

### Pub/Sub トピックの作成

各エクスポートタイプ（日次、週次、月次）に対してPub/Subトピックを作成します：

```bash
gcloud pubsub topics create daily-export-topic
gcloud pubsub topics create weekly-export-topic
gcloud pubsub topics create monthly-export-topic
```

### Cloud Functions へのデプロイ

各関数を第2世代のCloud FunctionsにPub/Subトリガーでデプロイします：

```bash
# 日次エクスポート関数のデプロイ
gcloud functions deploy daily_export \
  --gen2 \
  --runtime=python39 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=daily_export \
  --trigger-topic=daily-export-topic \
  --service-account=bq-sheets-exporter@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --memory=512MB \
  --timeout=540s

# 週次エクスポート関数のデプロイ
gcloud functions deploy weekly_export \
  --gen2 \
  --runtime=python39 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=weekly_export \
  --trigger-topic=weekly-export-topic \
  --service-account=bq-sheets-exporter@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --memory=512MB \
  --timeout=540s

# 月次エクスポート関数のデプロイ
gcloud functions deploy monthly_export \
  --gen2 \
  --runtime=python39 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=monthly_export \
  --trigger-topic=monthly-export-topic \
  --service-account=bq-sheets-exporter@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --memory=512MB \
  --timeout=540s
```

注：必要に応じて `--region` フラグの値を変更してください。

### Cloud Scheduler の設定

各関数に対して Cloud Scheduler ジョブを作成し、Pub/Subトピックにメッセージを発行するように設定します：

```bash
# 日次ジョブ
gcloud scheduler jobs create pubsub daily_export_job \
  --schedule "0 1 * * *" \
  --topic daily-export-topic \
  --message-body "Run daily export" \
  --time-zone "Asia/Tokyo" \
  --location asia-northeast1

# 週次ジョブ（毎週月曜日の午前1時に実行）
gcloud scheduler jobs create pubsub weekly_export_job \
  --schedule "0 1 * * 1" \
  --topic weekly-export-topic \
  --message-body "Run weekly export" \
  --time-zone "Asia/Tokyo" \
  --location asia-northeast1

# 月次ジョブ（毎月1日の午前1時に実行）
gcloud scheduler jobs create pubsub monthly_export_job \
  --schedule "0 1 1 * *" \
  --topic monthly-export-topic \
  --message-body "Run monthly export" \
  --time-zone "Asia/Tokyo" \
  --location asia-northeast1
```

## 設定

`config.yml` ファイルを更新してプロジェクトを設定します：

```yaml
project_id: "あなたのプロジェクトID"

queries:
  daily:
    - file: "queries/daily/query1.sql"
      sheet_id: "あなたのシートID-1"
  weekly:
    - file: "queries/weekly/query1.sql"
      sheet_id: "あなたのシートID-2"
  monthly:
    - file: "queries/monthly/query1.sql"
      sheet_id: "あなたのシートID-3"
```

## トラブルシューティング

- Cloud Functions で使用されるサービスアカウントが BigQuery と Google Sheets に必要な権限を持っていることを確認してください。
- エラーメッセージについては Cloud Functions のログを確認してください。
- `queries/` ディレクトリ内の SQL クエリが有効で、BigQuery のセットアップと互換性があることを確認してください。
- Pub/Sub トピックが正しく設定されていることを確認してください。
- Cloud Scheduler ジョブが正しく設定され、適切な Pub/Sub トピックにメッセージを送信していることを確認してください。

より詳細なトラブルシューティングについては、[Cloud Functions](https://cloud.google.com/functions/docs/troubleshooting)、[Cloud Scheduler](https://cloud.google.com/scheduler/docs/troubleshooting)、[Pub/Sub](https://cloud.google.com/pubsub/docs/troubleshooting) の Google Cloud ドキュメントを参照してください。