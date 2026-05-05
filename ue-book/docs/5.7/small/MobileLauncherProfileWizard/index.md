# Mobile Launcher Profile Wizard

> Wizard for mobile packaging scenarios

| 属性 | 值 |
|---|---|
| 分类 | Misc (Editor) |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | MobileLauncherProfileWizard (Editor) |
| 创建时间 | 2016-07-19 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MobileLauncherProfileWizard) | |

## 用途

这个 Plugin 为 UE5 的 **Project Launcher**（项目启动器）注册移动端打包向导，帮助开发者快速创建用于 **移动端 DLC / 云端内容分发** 的 Launcher Profile。

当你需要将手游拆分为「最小安装包 + 云端下载内容」的分发模式时（即使用 `BuildPatchServices` 模块），需要手动配置大量 Launcher Profile 参数。这个 Plugin 的作用就是用一个 **分步向导 UI** 自动完成这些配置，一次性生成两个 Profile：

1. **App Profile** — 生成一个尽可能小的 APK/IPA，仅包含引擎、游戏代码和下载界面所需的最少资产
2. **DLC Profile** — 将游戏内容 Cook 后打包为 HTTP Chunk 文件，供云端 CDN 分发

两个 Wizard（Android 和 iOS）在模块启动时通过 `ILauncherProfileManager::RegisterProfileWizard()` 注册，之后会在 Project Launcher 的「自定义配置文件」面板中以「新建配置文件」向导的形式出现。

## 使用场景

- 你在做一款移动端游戏，希望首次安装包尽可能小（几十 MB），大部分游戏内容在首次启动时通过 HTTP 下载 → 用这个 Wizard 自动生成 App + DLC 两个 Profile
- 你需要为 Android 多纹理格式（ETC2, ASTC 等）分别打包 DLC 内容 → Wizard 的 DLC 页面会列出平台支持的所有纹理格式供你选择
- 你要为 iOS App Store 提交最小化包体，同时通过云端分发关卡和资产 → 选择 iOS Wizard

## 使用流程

本 Plugin **没有蓝图接口和 C++ 公开 API**，完全通过编辑器 UI 操作：

### 启动向导

1. 打开 UE5 编辑器
2. 进入 **Platforms → Project Launcher**（或 **Platforms → Launch Profiles**）
3. 点击 **+ 新建配置文件** 旁的下拉箭头，选择：
   - **Minimal Android APK + DLC...** — Android 向导
   - **Minimal IOS App + DLC...** — iOS 向导

### 向导步骤

向导窗口（940×540 固定大小）分为 3 个步骤页面：

#### 第 1 步：选择输出目录

- 指定构建产物和 HTTP Chunk 文件的存储路径
- 可以手动输入或点击 **Browse...** 浏览选择
- 输出目录结构：
  ```
  <你选择的目录>/
  ├── App/1.0/          ← App Profile 的归档
  └── HTTPchunks/DLC1.0/  ← DLC Profile 的 HTTP Chunk 文件
  ```

#### 第 2 步：配置 Application Profile

- 选择 **Build Configuration**（Debug / DebugGame / Development / Shipping / Test）
- 从项目可用地图列表中勾选要随安装包一起分发的地图（通常只需一个启动地图）
- 该地图应包含一个 Level Blueprint 来启动 `BuildPatchServices` 下载流程，以及显示下载进度的 UMG UI

#### 第 3 步：配置 DLC Profile

- **Android**：选择要支持的纹理格式（如 ETC2, ASTC 等），用户的设备会自动下载最适合的格式
- **iOS**：纹理格式由平台决定，无需选择
- 从项目可用地图列表中勾选要包含在 DLC 中的地图
- 提供 **All / None** 快捷选择链接

#### 完成

- 点击 **Create Profile** 按钮
- 向导自动创建两个 Launcher Profile 并保存为 JSON 配置
- Profile 命名规则：`<项目名> - Android APK` / `<项目名> - Android DLC`（iOS 类似）
- 如果同名 Profile 已存在，自动追加数字后缀

### 生成的 Profile 配置详情

#### App Profile 配置

| 设置项 | 值 |
|---|---|
| Build Mode | Auto |
| Cook Mode | ByTheBook |
| 目标平台 | `Android_ETC2` 或 `IOS` |
| Release Version | `1.0` |
| Incremental Cook | None |
| 压缩 | 否 |
| 使用 UnrealPak | 是 |
| 打包方式 | Locally |
| 归档 | 是 → `<目录>/App/1.0/` |
| 部署 | DoNotDeploy |
| 启动 | DoNotLaunch |

#### DLC Profile 配置

| 设置项 | 值 |
|---|---|
| Build Mode | **DoNotBuild**（不重新编译） |
| Cook Mode | ByTheBook |
| 基于 Release Version | `1.0` |
| 创建 DLC | 是，名称 `DLC1.0` |
| 包含引擎内容 | 是 |
| HTTP Chunk 数据 | 是，Release 名称 `DLC1.0` |
| HTTP Chunk 目录 | `<目录>/HTTPchunks/DLC1.0/` |
| 打包方式 | DoNotPackage |
| 部署 | DoNotDeploy |
| 启动 | DoNotLaunch |

## C++ 用法

本 Plugin 是纯 Editor 模块，不提供可被其他模块直接使用的 C++ API。其公共接口 `IMobileLauncherProfileWizardModule` 仅提供模块加载检查：

### 头文件引入

```cpp
#include "IMobileLauncherProfileWizard.h"
```

### 检查模块可用性

```cpp
if (IMobileLauncherProfileWizardModule::IsAvailable())
{
    // 模块已加载
}
```

> **注意**：这个模块在 `StartupModule` 中通过 `ILauncherServicesModule::ProfileManagerInitializedDelegate` 注册两个 Wizard 到 Profile Manager，无需使用者手动调用任何注册逻辑。

## 内部架构

本 Plugin 的代码结构如下：

| 文件 | 职责 |
|---|---|
| `MobileLauncherProfileWizard.cpp` | 模块入口，注册 Android/iOS 两个 Wizard |
| `AndroidProfileWizard.cpp/.h` | Android Wizard 实现，配置 `Android_ETC2` 平台的 Profile |
| `IOSProfileWizard.cpp/.h` | iOS Wizard 实现，配置 `IOS` 平台的 Profile |
| `SProfileWizardUI.cpp/.h` | 共用的 Slate 向导 UI（3 步页面） |

两个平台 Wizard 的逻辑几乎完全对称，区别仅在于：
- 平台名称和纹理格式
- Android DLC 需要选择纹理 Cook Flavor（多纹理格式支持），iOS 则由平台决定
- Profile 命名后缀不同（`- Android APK` vs `- IOS App`）

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `LauncherServices` | Launcher Profile Manager 接口，用于注册 Wizard 和创建 Profile |
| `CoreUObject` | UObject 基础设施 |
| `TargetPlatform` | 平台信息查询（纹理格式等） |
| `DesktopPlatform` | 文件夹浏览对话框 |
| `Json` | Profile JSON 序列化 |
| `Slate` / `SlateCore` | 向导 UI 框架 |
| `InputCore` | 输入处理 |
| `AppFramework` | 应用框架支持 |
| `Projects` | 项目信息查询 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-04-16 | `819d4140` | 新增增量 Cook 和 Zen Snapshot 导入选项 — 说明该 Wizard 仍在随引擎功能演进更新 |
| 2024-05-01 | `a2b56134` | Slate: 废弃 `SListView::ItemHeight` 等接口 — 被动适配 Slate API 变更 |
| 2023-01-16 | `bbc37aa2` | IWYU 头文件清理 — 编译优化，非功能性变更 |

### 维护评价

- **创建时间**：2016 年 7 月，已有近 10 年历史
- **更新频率**：最近一次功能性更新在 2025-04-16，说明仍在随引擎迭代
- **维护状态**：**维护中** — 虽然更新不频繁，但功能稳定且在 UE 5.6 中仍被默认启用
- **代码质量**：逻辑清晰，Android/iOS 对称实现，但没有自动化测试
- **推荐使用**：如果你的移动端项目需要 DLC / 云端内容分发，这是官方提供的最便捷的 Profile 创建方式。由于代码量小且逻辑简单，即使需要自定义也可以直接 fork 修改

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MobileLauncherProfileWizard)
- [官方文档](https://docs.unrealengine.com/)（.uplugin 中未提供特定文档链接）
