# 番茄免费小说 7.4.5.32（74532）适配说明

## 版本与校验信息

- 目标宿主包名：`com.dragon.read`
- 目标宿主版本：`7.4.5.32`（`versionCode: 74532`）
- 目标宿主基准 APK SHA-256：`5afa20fe3b944cd9b80301187e87745a1bb4729778d0edb0d1a123c54df70176`
- 模块包名：`com.sheopeard.fanqiecustomizer`
- 模块版本：`5.0.5.74532`（`versionCode: 25`）
- 本地签名成品包（`build\74532\fanqie-customizer-5.0.5.74532.apk`）SHA-256：`FF6462AFF54470BB34695942BBE5795BEA46BCD7695986A13B7E945B8C26E092`（`apksigner verify` v3 通过）
- 云端无签名构建产物（`build\cloud-74532\fanqie-customizer-5.0.5.74532-unsigned.apk`）SHA-256：`2d53d22567977f8b2dd096219968d03661efe0d8744a603c9ed2b781316cf4f7`

## 7.4.3.32 -> 7.4.5.32 主要适配变更

1. **版本门控与清单**：
   - `TargetVersion` 与 `AndroidManifest.xml` 更新至 `74532L` / `7.4.5.32`（模块 `versionName="5.0.5.74532"`, `versionCode="25"`）。
2. **阅读页广告与弹窗拦截（`ReaderAdHooks` / `ReaderAdRules` / `ReaderBannerHooks`）**：
   - 阅读页横幅开关 `com.dragon.read.reader.extend.banner.a.b()Z` 迁移为 `c()Z`（7.4.5.32 中 `b(Z)V` 为关闭横幅方法）；`op6.a` -> `et6.a`；配置类 `jt7.z0` 高度读取/写入 `D/F` -> `bx7.z0.E/H`。
   - 翻页拦截器参数 `ft7.b` -> `xw7.b`；`interceptors.b.f` 改为 `interceptors.b$a`，通过 `field(field(receiver,"f"),"a")` 解析 `NsReaderActivity`。
   - 插屏与队列弹窗类迁移：`rc3.f/c/b` -> `nd3.f/c/b`，延迟首页弹窗 `el6.b/b$a` -> `uo6.b/b$a`，直播预览窗 `ii.a` -> `hi.a`，`LiveAdImpl.enterLiveRoom` 参数 `lt1.b` -> `it1.b`，`AdUtil.b` 参数 `qd3.a` -> `me3.a`，`parserlevel.model.page.a.W` -> `e0`。
   - 原生页广告视图父类 `Loi3/a;` -> `Llj3/a;`（用于 `tests/apk-contract-74532.json` 校验）。
3. **主界面底栏、启动页、发帖入口与挂件（`BottomNavigationHooks` / `StartupTabHooks` / `PostShortcutRules` / `ModuleHook` / `NativeUiHooks`）**：
   - 底栏按钮接口 `so7.g` -> `ks7.g`，`BottomTabBarLayout.J1/K1` -> `p3/r3`，`MainFragmentActivity.l2/R1/r2/s2/G2` -> `n2/S1/s2/t2/K2`。
   - 启动页标签容器 `pages.main.q4` -> `pages.main.b5`。
   - 发帖悬浮入口根视图 `sf5.m` -> `ei5.m`；挂件控制 `PendantController.t` -> `s`。
4. **“我的”原生卡片、书城频道、搜索直达与短剧恢复（`NativeUiHooks` / `FeatureHooks` / `DramaResumeHooks` / `BookTools`）**：
   - 卡片转换与渲染：`ye4.c/h` -> `wf4.c/h`、`yx3.d` -> `uy3.d`、`hf4.e` -> `fg4.e`、`k26.d/e/f` -> `l56.d/e/f`、`PolarisCardWrapper` 与 `card.model.b1` 视图 getter `b()` -> `c()`。
   - 书城频道：`NewBookMallFragment.li` -> `ni`，频道数据加载 `e34.b` -> `a44.b`。
   - 章末看视频免广告入口：`n33.c0.g1/d1` -> `b43.c0.k1/h1`。
   - 搜索直达：`FanqieSearchActivity.t2` 从单参改为双参 `(Lbk4/b;, GetSearchPageRequest)`，匹配参数个数更新为 `2`。
   - 短剧自动恢复：`hh6.e0/e0$c/f0` -> `xk6.e0/e0$c/f0`。
5. **构建脚本兼容性（`build.ps1`）**：
   - 显式加载 `System.IO.Compression` 程序集以兼容 Windows PowerShell 5.1 中的 `[System.IO.Compression.ZipArchiveMode]`。

## 静态与构建验证结果

- DEX/资源合约校验（`python tools/verify_target_apk.py analysis/74532/fanqie-7.4.5.32.apk`）：
  - `PASS: 113 method and 31 field contracts`
  - `PASS: 17 view class contracts`
- 单元测试（`.\test.ps1`）：14 项测试全部通过（`BookRulesTest`、`BottomNavigationRulesTest`、`DramaResumeRulesTest`、`FeatureHooksTest`、`LauncherVisibilityTest`、`NativeUiHooksTest`、`PostShortcutRulesTest`、`PrivacyRulesTest`、`ReaderAdRulesTest`、`RulesTest`、`StartupTabRulesTest`、`TabletRulesTest`、`TargetVersionTest`、`UpdatePopupRulesTest`）。
- 打包与签名验证（`.\build.ps1` 与 `python tools/build_unsigned.py`）：签名 APK（v3 验证通过）与无签名 APK 均已生成。
- 实机运行时验证：静态 DEX 与单元测试无法替代真机 LSPosed 运行时测试，请安装到测试机并覆盖番茄 `7.4.5.32` 验证底栏、书架、阅读横幅/插屏/直播弹窗、我的卡片与更新弹窗抑制效果。
