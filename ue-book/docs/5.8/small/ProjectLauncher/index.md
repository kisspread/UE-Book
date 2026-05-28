# Project Launcher

> Configure custom project launch profiles.

| 属性 | 值 |
|---|---|
| 中文名 | 项目启动器 |
| 分类 | Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ProjectLauncher` (Editor), `CommonLaunchExtensions` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-04-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher) | |

## 用途

此插件专为 `UnrealFrontend` 程序设计，用于配置和管理自定义的项目启动配置文件。它并非通用的编辑器插件，而是为项目的构建、打包、部署流程提供了一个深度可定制的启动配置界面。通过 `LaunchProfile` 和 `TreeBuilder` 等核心概念，允许开发者精细地控制项目启动的各个环节，例如选择特定的构建目标、配置部署选项、管理插件和地图等。

## 使用场景

- **为不同团队成员定制启动配置**：美术、策划和程序员可能需要不同的启动设置（如不同的编辑器功能、插件集合），此插件允许为每个角色保存和管理专属配置。
- **自动化构建与部署流程**：在 UnrealFrontend 的自动化测试或 CI/CD 管线中，使用预定义的启动配置来执行标准化的打包、部署和测试流程。
- **管理复杂的多平台部署**：需要为同一个项目配置针对不同目标平台（如 Win64、Linux、Mac）的启动和部署参数。
- **精细控制构建内容**：需要排除特定插件、只包含特定地图或资产进行构建时，通过此插件进行图形化配置。

## 蓝图用法

本插件主要作为编辑器扩展 (`UnrealFrontend`) 使用，未提供面向运行时游戏逻辑的蓝图 API。其核心功能（如 `LaunchProfile` 的创建与编辑）通过 `UnrealFrontend` 程序的图形界面或 C++ 代码进行操作。

## C++ 用法

普通游戏项目通常不直接引用此插件的模块，它主要服务于 `UnrealFrontend` 工具链。若要在 `UnrealFrontend` 的扩展开发中使用，可参考以下方式。

### 头文件引入

```cpp
#include "ProjectLauncher.h"
#include "CommonLaunchExtensions.h"
```

### 基本用法 (编辑器扩展)

```cpp
// 在 UnrealFrontend 的扩展模块中，可以访问和操作 LaunchProfile 数据
#include "Interfaces/ILauncherProfileManager.h"

// 获取启动配置文件管理器
ILauncherProfileManager* ProfileManager = FModuleManager::GetModuleChecked<IProjectLauncherModule>("ProjectLauncher").GetProfileManager();
if (ProfileManager)
{
    // 获取或创建启动配置
    TSharedRef<FLaunchProfile> NewProfile = ProfileManager->CreateNewProfile(TEXT("MyCustomBuild"));
    // 配置此 profile 的参数 (例如构建配置， 部署平台等)
    // NewProfile->SetBuildConfiguration(EBuildConfiguration::Development);
    // ...
    ProfileManager->SaveProfile(NewProfile);
}
```

## Demo 示例

以下示例展示了如何在 `UnrealFrontend` 的扩展模块中注册一个自定义的启动扩展。

```cpp
// MyCustomLaunchExtension.h
#pragma once

#include "CommonLaunchExtensions/Interfaces/ILaunchExtension.h"

class FMyCustomLaunchExtension : public ILaunchExtension
{
public:
    virtual void Initialize() override;
    virtual void CustomizeLauncherProfile(FLaunchProfile& Profile) override;
};

// MyCustomLaunchExtension.cpp
#include "MyCustomLaunchExtension.h"

void FMyCustomLaunchExtension::Initialize()
{
    // 初始化逻辑
}

void FMyCustomLaunchExtension::CustomizeLauncherProfile(FLaunchProfile& Profile)
{
    // 在这里修改传入的 Profile 对象
    // 例如，强制添加某个插件或设置某个变量
    Profile.AddPlugin(TEXT("MyEssentialPlugin"));
}
```

## 模块依赖

本插件的模块仅用于 `UnrealFrontend`，普通项目无需依赖。其内部构建依赖已处理。无特殊依赖（仅标准 Core、Slate、Editor 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4225c8f8` | Remove the restriction from Project Launcher that prevents package & deploy to be specified together | 允许同时指定“打包”和“部署”选项，增加了灵活性 |
| 2026-04-27 | `77966850` | Launcher2: Use the value of bUseZenStore from ProjectSettings when deciding whether to pass -ZenStor | 读取项目设置来决定是否传递 ZenStore 参数 |
| 2026-04-17 | `921928f4` | Add support for skipping content when downloading staged build via Project Launcher 2 Build Sync ext | 在构建同步扩展中支持跳过部分内容的下载 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明若干开发者模块仅支持桌面平台 |
| 2026-04-14 | `c58ad33c` | Project Launcher now allows you to select maps that are in plugins. | 现在允许选择位于插件目录下的地图 |

### 维护评价

**积极维护中**。该插件创建于约 2025 年 4 月，非常年轻。从近期（2026年4月）的提交记录来看，更新非常频繁且活跃，主要集中在功能增强和 Bug 修复上（如增加部署灵活性、集成新特性、修复平台限制等）。`.uplugin` 中标记为 `IsBetaVersion=true`，表明它仍处于开发和完善阶段。鉴于其持续的功能迭代和针对 `UnrealFrontend` 工具链的明确目标，**推荐在需要定制前端启动配置的开发流程中使用**，但需注意其 API 可能随 Beta 版本更新而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher)
- [官方文档](https://docs.unrealengine.com/) (插件本身无独立文档，相关信息参考 UnrealFrontend 使用指南)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (通常位于此目录下)