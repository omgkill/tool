from parser_service.pipeline.pipeline import Pipeline


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'crawl':
        start_url = sys.argv[2] if len(sys.argv) > 2 else 'https://go.dev/doc/'
        max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        
        # 创建pipeline配置
        config = {
            'max_pages': max_pages
        }
        
        # 创建pipeline
        pipeline = Pipeline(config)
        
        # 运行pipeline
        result = pipeline.run(start_url)
    else:
        print("使用方式:")
        print("  py -3.11 app_pipeline.py crawl <URL> [max_pages]")
        print("")
        print("示例:")
        print("  py -3.11 app_pipeline.py crawl https://go.dev/doc/")
        print("  py -3.11 app_pipeline.py crawl https://go.dev/doc/ 10")


if __name__ == '__main__':
    main()
