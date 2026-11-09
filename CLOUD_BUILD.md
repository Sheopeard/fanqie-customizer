# 云端构建接口

`tools/build_unsigned.py` 只生成未签名 APK，支持 Linux 和 Windows，不读取或创建私钥。固定使用 JDK 17、Android platform 36 和 Build Tools 36.0.0，核对 libs 内的依赖校验和，并在全新的临时目录构建及运行所有 Java 规则测试。

```powershell
python tools/build_unsigned.py --sdk <SDK目录> --jdk <JDK目录> --output build/cloud
```

输出为未签名 APK、`build-result.json` 和测试日志。未签名包不能直接安装；正式签名沿用已有密钥，不能生成新密钥代替。`build.ps1` 现在在原密钥缺失时立即报错。

完整试点在用户的私有 `android-adaptation-lab` 仓库运行，APK 输入和分析资料不上传本公开源码仓库。私有流程固定本仓库提交及项目适配契约，只有已审核基线才允许构建；未知版本生成差异和映射候选，等待代码适配及审核，不自动放开版本门禁。

静态通过的候选包不等于手机已验收。安装、LSPosed 设置、重启目标应用和实际效果确认仍由用户操作。
