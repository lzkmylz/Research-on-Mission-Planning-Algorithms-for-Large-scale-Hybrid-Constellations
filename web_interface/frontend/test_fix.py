#!/usr/bin/env python3
"""
验证前端修复测试
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    console_logs = []
    page_errors = []
    page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("=" * 60)
    print("前端修复验证测试")
    print("=" * 60)

    # 访问首页
    print("\n[TEST] 访问首页...")
    try:
        page.goto('http://localhost:5173', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(5000)
        title = page.title()
        print(f"  ✓ 页面加载成功")
        print(f"  ✓ 页面标题: {title}")
    except Exception as e:
        print(f"  ✗ 页面加载失败: {e}")
        browser.close()
        exit(1)

    # 检查 Vue 是否渲染
    print("\n[TEST] 检查 Vue 渲染...")
    try:
        # 检查 #app 是否有内容
        app_content = page.evaluate("""() => {
            const app = document.getElementById('app');
            return {
                exists: !!app,
                html: app ? app.innerHTML.substring(0, 1000) : null,
                hasContent: app && app.innerHTML.length > 100
            };
        }""")

        print(f"  #app 存在: {app_content['exists']}")
        print(f"  #app 有内容: {app_content['hasContent']}")

        if app_content['hasContent']:
            print(f"  ✓ Vue 应用已成功渲染！")
            print(f"  内容预览: {app_content['html'][:200]}...")
        else:
            print(f"  ✗ Vue 应用未渲染")
            print(f"  HTML: {app_content['html']}")
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")

    # 检查页面错误
    print("\n[TEST] 检查页面错误...")
    if page_errors:
        print(f"  ✗ 发现 {len(page_errors)} 个错误:")
        for err in page_errors[:5]:
            print(f"    {err}")
    else:
        print("  ✓ 无 JavaScript 错误")

    # 检查控制台日志
    print("\n[TEST] 检查控制台日志...")
    if console_logs:
        print(f"  发现 {len(console_logs)} 条日志:")
        for log in console_logs[:10]:
            print(f"    {log}")
    else:
        print("  无控制台日志")

    # 截图
    print("\n[TEST] 生成截图...")
    try:
        page.screenshot(path='/tmp/frontend_after_fix.png', full_page=True)
        print(f"  ✓ 截图已保存: /tmp/frontend_after_fix.png")
    except Exception as e:
        print(f"  ✗ 截图失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    browser.close()
