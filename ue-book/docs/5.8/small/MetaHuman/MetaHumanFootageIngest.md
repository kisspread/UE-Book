# MetaHuman Footage Ingest

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 镜头导入管理器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器UI组件， 捕捉源管理， 镜头导入逻辑） |
| 模块 | `MetaHumanFootageIngest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | （无法计算， 创建时间未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest) | |

## 用途

MetaHuman Footage Ingest 是 MetaHuman Animator 插件套件中的一个**编辑器UI模块**，其核心功能是提供一个集成的编辑器界面，用于**管理各种捕捉设备（如 iPhone）、预览捕捉的镜头素材（Take），并将其导入（Ingest）到 Unreal Engine 项目中**。

它解决的问题是：在复杂的 MetaHuman 面部动画制作流程中，用户需要处理来自不同设备和多机位的原始拍摄数据。此插件提供了一个统一的“捕获管理器”(Capture Manager) 面板，让用户能够：
1.  **发现和连接**支持的捕捉设备。
2.  **浏览和筛选**设备上或本地存储的拍摄素材。
3.  **预览**素材的缩略图和元数据。
4.  **选择性导入**所需的素材到项目中指定的路径，并自动创建对应的 `UFootageCaptureData` 资产。

**重要提示**：从 **5.7 版本开始**，此模块已被标记为**废弃 (Deprecated)**，其功能已迁移至 `CaptureManager` 模块。本描述基于其遗留代码和功能。

## 使用场景

- **场景一：面部动画捕捉**：你使用 iPhone 配合 Live Link Face App 进行了面部表情捕捉，需要将 `.usdc` 格式的捕捉文件导入引擎进行后续的 MetaHuman 角色驱动。
- **场景二：多机位拍摄管理**：你的项目使用了多个专业相机从不同角度拍摄演员表演，需要通过此管理器统一导入这些镜头素材，并管理其对应的 `CaptureData` 资产。
- **场景三：团队协作**：需要将其他团队成员拍摄并存储在共享路径下的捕捉数据，方便地引入到自己的工程中。

## 蓝图用法

此插件主要提供**编辑器扩展和工具面板**，而非直接在运行时蓝图中使用的节点。其核心逻辑封装在 Slate Widget 和编辑器工具中。

### 核心类与功能

| 功能 | 说明 | 所在类 |
|---|---|---|
| `FCaptureManager::Show()` | 启动并显示“捕获管理器”编辑器窗口（如果已初始化）。 | `FCaptureManager` |
| `SCaptureManagerWidget` | 整个捕获管理器的主窗口，整合了捕捉源列表和镜头导入界面。 | `SCaptureManagerWidget` |
| `SCaptureSourcesWidget` | “捕捉源”列表面板，显示和管理已配置的捕捉源。 | `SCaptureSourcesWidget` |
| `SFootageIngestWidget` | “镜头导入”面板，用于预览Take、管理导入队列和执行导入。 | `SFootageIngestWidget` |
| `SaveImportedAssets()` | 将本次导入创建的所有资产保存到磁盘（受自动保存设置影响）。 | `SFootageIngestWidget` |

## C++ 用法

此模块的C++ API主要用于编辑器扩展，底层依赖 `MetaHumanCaptureSource` 和 `MetaHumanImageViewerEditor` 模块。

### 头文件引入

```cpp
#include "MetaHumanFootageIngest/CaptureManager.h"
#include "MetaHumanFootageIngest/FootageIngestWidget.h"
```

### 基本用法：显示捕获管理器窗口

这是最常见的用法，通过单例启动整个UI。
*(来源: `Public/CaptureManager.h`, `Public/CaptureManager.cpp`)*

```cpp
// 确保模块已启动（通常由编辑器自动加载）
if (FMetaHumanFootageIngestModule* Module = FModuleManager::GetModulePtr<FMetaHumanFootageIngestModule>(TEXT("MetaHumanFootageIngest")))
{
    // 获取管理器单例并显示窗口
    if (FCaptureManager* CaptureManager = FCaptureManager::Get())
    {
        CaptureManager->Show();
    }
}
```

### 进阶用法：自定义捕捉源筛选逻辑

在 `SCaptureSourcesWidget` 中，你可以通过 `FDevelopersContentFilter` 来控制是否在列表中显示“开发者内容”路径下的资产。
*(来源: `Private/DevelopersContentFilter.h`)*

```cpp
// 创建一个过滤器，隐藏当前用户和其它用户的开发者内容
UE::MetaHuman::FDevelopersContentFilter Filter(
    UE::MetaHuman::EDevelopersContentVisibility::NotVisible,
    UE::MetaHuman::EOtherDevelopersContentVisibility::NotVisible
);

// 假设你有一个资产路径
FString AssetPath = TEXT("/Game/MyProject/Captures/MyCapture");
bool bPasses = Filter.PassesFilter(AssetPath); // 根据路径判断是否通过筛选
```

## Demo 示例

以下示例展示如何在你的编辑器模块中，当用户按下特定快捷键时，弹出捕获管理器窗口。

### MyEditorModule.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterCommands();
    void ShowCaptureManager();
};
```

### MyEditorModule.cpp

```cpp
#include "MyEditorModule.h"
#include "MetaHumanFootageIngest/CaptureManager.h" // 引入插件头文件
#include "Framework/Commands/UICommandList.h"

#define LOCTEXT_NAMESPACE "MyEditorModule"

void FMyEditorModule::StartupModule()
{
    RegisterCommands();
}

void FMyEditorModule::ShutdownModule()
{
    // 清理命令绑定
}

void FMyEditorModule::RegisterCommands()
{
    // 这里简化了命令注册流程。实际应使用 FUICommandInfo 和 FInputBindingManager。
    // 绑定一个快捷键，例如 Ctrl+Shift+C
    FInputBindingManager::Get().RegisterCommandMapping(
        TEXT("MyModule.ShowCaptureManager"),
        FInputChord(EModifierKey::Control | EModifierKey::Shift, EKeys::C),
        FExecuteAction::CreateRaw(this, &FMyEditorModule::ShowCaptureManager),
        FCanExecuteAction()
    );
}

void FMyEditorModule::ShowCaptureManager()
{
    // 调用插件的API
    if (FCaptureManager* CaptureManager = FCaptureManager::Get())
    {
        CaptureManager->Show();
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

你的模块（例如一个新的编辑器工具）若要使用 `MetaHumanFootageIngest` 的功能，需要在 `Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanFootageIngest` | 本模块，提供捕获管理器核心UI和逻辑。 |
| `MetaHumanCaptureSource` | 提供各种捕捉设备驱动（如LiveLink Face, iPhone等）的接口。 |
| `MetaHumanImageViewerEditor` | 提供图像序列查看器等编辑器组件，用于预览。 |
| `RHI` | 渲染硬件接口，用于缩略图生成和预览纹理创建。 |

## 维护状态

### 近期更新

根据提供的 git 历史，最近的提交均发生在 2026 年 5 月，但提交信息显示这些更新属于 `MetaHumanAnimator` 插件的其他核心模块（如导出序列、身体追踪、缓存修复），**并非直接针对 `MetaHumanFootageIngest` 模块的功能更新或修复**。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题。 |

### 维护评价

**已废弃 (Deprecated)**。

1.  **创建时间**：未知，但属于早期 MetaHuman Animator 工具链的一部分。
2.  **近期更新**：**无实质性功能更新**。最近的提交与本模块无关。
3.  **活跃维护**：**否**。从 **5.7 版本开始**，该模块已被正式标记为 `UE_DEPRECATED(5.7, ...)`，明确指出功能已迁移至 `CaptureManager` 模块。这意味着 Epic 不再为此模块添加新功能，可能仅会进行维持编译通过的最小维护或安全修复。
4.  **已知问题/限制**：主要限制是**已废弃**。代码中大量使用 `PRAGMA_DISABLE_DEPRECATION_WARNINGS`，提醒开发者避免在新项目中依赖它。
5.  **推荐使用**：**不推荐在新项目中使用**。对于新项目或正在升级到 UE 5.7+ 的项目，应直接使用官方推荐的 `CaptureManager` 模块。本文档仅作为遗留系统的历史参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/)(应搜索 MetaHuman Animator 或 Capture Manager 相关部分)