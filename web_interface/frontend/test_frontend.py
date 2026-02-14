#!/usr/bin/env python3
"""
前端功能测试脚本
"""
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Capture console logs
    console_logs = []
    page_errors = []
    page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("=" * 60)
    print("前端功能测试")
    print("=" * 60)

    # 测试1: 访问首页
    print("\n[TEST 1] 访问首页...")
    try:
        page.goto('http://localhost:5173')
        page.wait_for_load_state('networkidle', timeout=15000)
        # 额外等待 Vue 应用渲染 - 给更多时间
        page.wait_for_timeout(8000)
        title = page.title()
        print(f"  ✓ 页面加载成功")
        print(f"  ✓ 页面标题: {title}")

        # 检查页面是否有错误
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        if page_errors:
            print(f"  ⚠ 页面 JavaScript 错误: {len(page_errors)} 个")
            for err in page_errors[:3]:
                print(f"    - {err}")
    except Exception as e:
        print(f"  ✗ 页面加载失败: {e}")
        browser.close()
        exit(1)

    # 测试2: 检查页面元素
    print("\n[TEST 2] 检查页面元素...")
    try:
        # 等待页面内容加载
        page.wait_for_selector('.hero, .home, h1', timeout=10000)

        buttons = page.locator('button').all()
        print(f"  ✓ 发现 {len(buttons)} 个按钮")

        links = page.locator('a[href]').all()
        print(f"  ✓ 发现 {len(links)} 个链接")

        inputs = page.locator('input, textarea, select').all()
        print(f"  ✓ 发现 {len(inputs)} 个输入框")

        # 获取页面文本内容
        headings = page.locator('h1, h2, h3').all()
        if headings:
            print(f"  ✓ 发现 {len(headings)} 个标题:")
            for h in headings[:3]:
                text = h.inner_text().strip()
                if text:
                    print(f"    - {text[:50]}")

        # 检查页面主要内容
        page_text = page.inner_text('body')
        if '星座任务规划系统' in page_text:
            print(f"  ✓ 页面主要内容已加载")
        else:
            print(f"  ⚠ 未找到预期页面内容")

    except Exception as e:
        print(f"  ✗ 元素检查失败: {e}")

    # 测试3: 检查 API 连通性
    print("\n[TEST 3] 检查后端 API 连通性...")
    try:
        import urllib.request
        req = urllib.request.Request('http://localhost:8000/api/health')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 'healthy':
                print(f"  ✓ 后端 API 连通正常")
                print(f"  ✓ API 版本: {data.get('version', 'unknown')}")
            else:
                print(f"  ✗ API 响应异常: {data}")
    except Exception as e:
        print(f"  ✗ API 检查失败: {e}")

    # 测试4: 截图保存
    print("\n[TEST 4] 生成页面截图...")
    try:
        page.screenshot(path='/tmp/frontend_test.png', full_page=True)
        print(f"  ✓ 截图已保存: /tmp/frontend_test.png")
    except Exception as e:
        print(f"  ✗ 截图失败: {e}")

    # Debug: 输出页面内容
    print("\n[DEBUG] 页面 HTML 内容片段:")
    try:
        html = page.content()
        # 只显示 body 内容的前 1000 字符
        body_start = html.find('<body')
        body_end = html.find('</body>')
        if body_start > 0 and body_end > 0:
            body_content = html[body_start:body_end+7]
            print(body_content[:1000])
        else:
            print(html[:1000])
    except Exception as e:
        print(f"  无法获取页面内容: {e}")

    # Debug: 检查 Vue 是否挂载
    print("\n[DEBUG] 检查 Vue 挂载状态:")
    try:
        vue_check = page.evaluate("""() => {
            const app = document.querySelector('#app');
            return {
                appExists: !!app,
                appInnerHTML: app ? app.innerHTML.substring(0, 500) : null,
                vueDevTools: typeof window.__VUE__ !== 'undefined',
                vueApp: !!document.querySelector('[data-v-app]')
            };
        }""")
        print(f"  #app 存在: {vue_check['appExists']}")
        print(f"  #app 内容: {vue_check['appInnerHTML'][:200] if vue_check['appInnerHTML'] else 'empty'}")
        print(f"  Vue DevTools: {vue_check['vueDevTools']}")
        print(f"  data-v-app 标记: {vue_check['vueApp']}")
    except Exception as e:
        print(f"  检查失败: {e}")

    # 测试5: 检查 Vue 组件加载
    print("\n[TEST 5] 检查 Vue 应用状态...")
    try:
        # 检查是否有 Vue 相关的 DOM 元素
        vue_elements = page.locator('[data-v-app], #app, .app').all()
        if vue_elements:
            print(f"  ✓ Vue 应用元素已加载")
        else:
            print(f"  ⚠ 未找到明确的 Vue 应用标记")
    except Exception as e:
        print(f"  ✗ Vue 检查失败: {e}")

    # Debug: 检查脚本加载状态
    print("\n[DEBUG] 检查脚本加载状态:")
    try:
        script_check = page.evaluate("""() => {
            const mainScript = document.querySelector('script[src*="main.js"]');
            return {
                mainScriptExists: !!mainScript,
                mainScriptSrc: mainScript ? mainScript.src : null,
                allScripts: Array.from(document.querySelectorAll('script')).map(s => ({
                    src: s.src,
                    type: s.type,
                    async: s.async,
                    defer: s.defer
                }))
            };
        }""")
        print(f"  main.js 存在: {script_check['mainScriptExists']}")
        print(f"  main.js 路径: {script_check['mainScriptSrc']}")
        print(f"  页面脚本总数: {len(script_check['allScripts'])}")
    except Exception as e:
        print(f"  检查失败: {e}")

    # 测试6: 检查控制台日志
    print("\n[TEST 6] 浏览器控制台日志...")
    if console_logs:
        print(f"  发现 {len(console_logs)} 条日志:")
        for log in console_logs[:10]:
            print(f"    {log}")
    else:
        print("  无控制台日志")

    # 检查页面错误
    print("\n[TEST 7] 页面 JavaScript 错误...")
    if page_errors:
        print(f"  发现 {len(page_errors)} 个错误:")
        for err in page_errors[:5]:
            print(f"    {err}")
    else:
        print("  无 JavaScript 错误")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    browser.close()
