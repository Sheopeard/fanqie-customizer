# 番茄 7.4.3.32 适配记录

2026-11-06 根据当前手机实际安装的番茄 APK 适配。番茄版本名为 `7.4.3.32`，versionCode 为 `74332`；模块更新为 `5.0.5.74332`，versionCode 为 `24`，只对该精确番茄版本加载规则。

## 主要变化

| 功能 | 新版入口或处理 |
|---|---|
| 底栏按钮 | `so7.g` 与 `BottomTabBarLayout.J1/K1` |
| 底栏动画与默认页 | `MainFragmentActivity.l2/X1/R1/s2/r2`，实际导航列表 `pages.main.q4.e` |
| 发帖浮钮 | `sf5.m` 构造及 `setVisibilitySafely` |
| 自动短剧续播 | `hh6.e0`，延迟调用 `hh6.f0` |
| 我的卡片 | `ye4.c.g`；刷新转换改用 `ye4.h.a`，过滤输入树并保留原生 List 返回值 |
| 收入卡片 | `b1.b()` 与 `PolarisCardWrapper.b()` 获取 View |
| 侧栏 | `hf4.e` 返回 `k26` 模型，分别过滤菜单、游戏及消息列表 |
| 书城频道 | `NewBookMallFragment.li` 和 `e34.b.a`，保留替换频道自己的请求 |
| 福利浮钮 | `MainFragmentActivity.G2` 及 SDK 展示入口 |
| 阅读横幅 | banner assistant `d/b/n/o`，高度配置 `jt7.z0.D/F` |
| 阅读插页 | 拦截器参数 `ft7.b`，保留阅读场景限制 |
| 插屏与广告队列 | `rc3.f/c/b`、`el6.b$a`、`ii.a`，函数式 popup 参数 `vi0.b` |
| 直播广告路由 | 参数类型 `lt1.b`、`qd3.a` |
| 章节末尾入口 | `n33.c0.g1/l1/d1`，只隐藏免广告类型入口 |
| 书籍编号搜索 | `FanqieSearchActivity.t2(cj4.b)`，原生搜索词字段仍为 `a` |
| 漫画广告 View | 新版 `CartoonOneStopAdView` 替代已移除的旧类 |
| 诊断 | 功能侧栏不再声明 `onVisible`，改记录其 `onCreateContent` |

## 验证结果

- 只读提取当前手机上的番茄 APK 和已安装模块备份；安装、卸载、启用及应用界面由用户操作。
- 番茄 APK SHA-256：`e5a07b30e9c92d2b7e9dcbb73a3ec44393d2e50689e70da5a7d3e9d6d3dc12de`。
- 旧 7.4.1.32 检查中有 58 项在新 APK 中不匹配，已按实际源码路径重新映射，未仅修改版本判断。
- `tests/apk-contract-74332.json` 的 113 项方法签名、30 项字段类型和 17 项界面类父类检查全部通过。
- 14 组 Java 规则测试通过。新增菜单清空后仍保留非空根对象和空列表、且不修改缓存的回归检查；版本测试明确拒绝旧宿主版本。
- JDK 17、SDK android-36、Build Tools 36.0.0 构建成功，APK 包名、版本及 v3 签名检查通过。
- APK SHA-256：`c9cb79c50e113a6361351ae7540deaa81502d0e3023f6ea6e063d17805303494`。

复验方法：

```powershell
python tools/verify_target_apk.py <番茄7.4.3.32.apk>
./build.ps1 -SdkRoot <AndroidSDK目录> -KeyStorePath <上次使用的本地签名文件>
./test.ps1 -SdkRoot <AndroidSDK目录>
```

## 安装与验收

新包沿用上次适配包的包名与签名。已核对当前手机上 `5.0.5.74132` 模块与新包的签名一致，可直接覆盖安装，无需卸载，可保留模块设置。作者签名的原版模块与此本地签名不同。

安装后由用户在 LSPosed 中确认模块启用、作用域选择番茄，再手动强行停止并重新打开番茄。依次检查底栏与启动页、书城频道、我的页面、各浮钮、阅读翻页和广告占位、章节末尾入口及编号搜索。

**手机界面尚未实际验收。** 静态检查和规则测试不能证明所有服务器卡片、动态广告模板及直播插件均生效；平板布局也未实测。需要诊断时由用户打开命中日志、复现并导出模块日志，分享前检查个人信息。

异常时先禁用模块并重开番茄。旧模块 APK 已在本机备份；如需卸载后回退，先记录模块设置。番茄应用本身无需卸载。

番茄 APK、反编译源码、设备资料和签名私钥均不提交到仓库。此前版本的记录保留在 `ADAPTATION-74132.md`。
