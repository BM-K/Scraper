# Scraper
언론사별 최신 기사 스크랩
- JTBC
- SBS
- NEWSIS
- NOCUT

## Crontab -e
*/5 * * * * /opt/conda/bin/python /workspace/Scraper/main.py --scraping_task jtbc --path_to_data /workspace/Scraper/jtbc_data --latest_config config.json > /workspace/Scraper/jtbc_cron.log 2>&1

*/5 * * * * /opt/conda/bin/python /workspace/Scraper/main.py --scraping_task sbs --path_to_data /workspace/Scraper/sbs_data --latest_config config.json > /workspace/Scraper/sbs_cron.log 2>&1

*/5 * * * * /opt/conda/bin/python /workspace/Scraper/main.py --scraping_task newsis --path_to_data /workspace/Scraper/newsis_data --latest_config config.json > /workspace/Scraper/newsis_cron.log 2>&1

*/5 * * * * /opt/conda/bin/python /workspace/Scraper/main.py --scraping_task nocut --path_to_data /workspace/Scraper/nocut_data --latest_config config.json > /workspace/Scraper/nocut_cron.log 2>&1
