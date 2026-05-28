# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHuman Toolkit` 模块是 MetaHuman Animator 插件的**基础编辑器工具包框架**。它并非直接面向最终用户的功能模块，而是为 MetaHuman 系列相关的资产编辑器（如 `MetaHuman Identity`、`MetaHuman Performance` 等）提供了一套标准化的、功能丰富的编辑器界面基础架构。

该模块的核心价值在于：
1.  **标准化编辑器布局**：提供一个集成了细节面板、时间轴（Sequencer）和高级视口的标准资产编辑器框架。
2.  **强大的 AB 对比视图**：在视口中内置了 AB 分屏、AB 擦除等高级对比模式，便于用户精确对比不同状态（如不同渲染模式、不同追踪结果）下的 MetaHuman 外观。
3.  **深度数据可视化**：内置深度网格组件，能够将深度图（如来自 LIDAR 或立体视觉）实时渲染为 3D 网格，方便在编辑器内检查深度数据。
4.  **序列器深度集成**：将媒体轨道（颜色、深度、音频）与序列器无缝集成，支持基于时间轴的动画预览和编辑。

简而言之，这个插件解决的问题是：**为所有 MetaHuman 内容创作工具提供一个统一、高效且功能强大的编辑器操作界面**。它的存在是为了确保 Epic 自家的各种 MetaHuman 资产编辑器拥有一致的用户体验和高级功能。

## 使用场景

*   你正在使用 **MetaHuman Identity** 资产创建角色，并希望在编辑器内实时对比不同材质渲染效果、不同面部姿态或追踪结果的准确性。 → 使用本插件提供的 AB 视图和视口工具。
*   你正在使用 **MetaHuman Performance** 资产，需要将一段面部捕捉视频（颜色+深度）和音频同步到序列器时间轴上进行预览和动画关键帧编辑。 → 使用本插件提供的媒体轨道管理和序列器集成。
*   你正在开发一个自定义的 MetaHuman 资产编辑器，希望快速获得一个包含视口、细节面板和时间轴的标准编辑器布局，并支持 AB 对比功能。 → 继承本模块提供的 `FMetaHumanToolkitBase` 类。

## 蓝图用法

本模块主要是 C++ 框架，提供给编辑器插件和工具使用，而非直接暴露给蓝图。其核心类（如 `FMetaHumanToolkitBase`, `FMetaHumanEditorViewportClient`）不包含 `UFUNCTION(BlueprintCallable)` 标记。功能主要通过 C++ 继承和重写来实现。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanToolkitBase.h"
#include "MetaHumanEditorViewportClient.h"
```

### 基本用法

创建一个继承自 `FMetaHumanToolkitBase` 的自定义资产编辑器工具包。
*来源：基于 `FMetaHumanToolkitBase` 类定义推断。*

```cpp
// MyAssetToolkit.h
#pragma once
#include "MetaHumanToolkitBase.h"

class FMyAssetToolkit : public FMetaHumanToolkitBase
{
public:
    FMyAssetToolkit(UAssetEditor* InOwningAssetEditor);
    virtual ~FMyAssetToolkit() override = default;

protected:
    // 重写以添加自定义的视口底部控件
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;
    
    // 重写以自定义 AB 视图菜单的内容
    virtual void HandleGetViewABMenuContents(EABImageViewMode InViewMode, FMenuBuilder& InMenuBuilder) override;

    // 重写以处理撤销/重做事务
    virtual void HandleUndoOrRedoTransaction(const FTransaction* InTransaction) override;
};
```

### 进阶用法

1.  **控制视口行为**：通过获取并配置 `FMetaHumanEditorViewportClient` 来精细控制视口。
    *来源：`FMetaHumanEditorViewportClient` 公共接口。*

```cpp
// 在 FMyAssetToolkit::PostInitAssetEditor 中
TSharedPtr<FMetaHumanEditorViewportClient> ViewportClient = GetMetaHumanEditorViewportClient();
if (ViewportClient.IsValid())
{
    // 设置深度数据的近远平面范围
    FMetaHumanViewportClientDepthData FootageDepthData(15.0f, 100.0f, 5.0f, 200.0f);
    ViewportClient->SetFootageDepthData(FootageDepthData);
    
    // 锁定2D导航模式
    ViewportClient->SetNavigationLocked(true);
    
    // 绑定组件点击事件
    ViewportClient->OnPrimitiveComponentClickedDelegate.BindLambda([](const UPrimitiveComponent* InComp)
    {
        UE_LOG(LogTemp, Log, TEXT("Clicked on component: %s"), *InComp->GetName());
    });
}
```

2.  **管理深度可视化**：使用 `FMetaHumanToolkitBase` 的接口创建和操控深度网格。
    *来源：`FMetaHumanToolkitBase` 中 `DepthMeshComponent` 相关方法。*

```cpp
// 在合适的时机（如加载深度数据后）
UCameraCalibration* CameraCalib = /* 获取相机标定数据 */;
CreateDepthMeshComponent(CameraCalib); // 创建深度网格可视化组件

UTexture* DepthTexture = /* 获取深度纹理 */;
SetDepthMeshTexture(DepthTexture); // 将深度纹理应用到网格上

// 当不再需要时
DestroyDepthMeshComponent(); // 销毁深度网格组件
```

## Demo 示例

一个最小化的自定义资产编辑器工具包，集成了基础功能并添加了一个简单的自定义视口控件。
*文件：`MyDemoToolkit.h` / `MyDemoToolkit.cpp`*

```cpp
// MyDemoToolkit.h
#pragma once
#include "MetaHumanToolkitBase.h"

class FMyDemoToolkit : public FMetaHumanToolkitBase
{
public:
    FMyDemoToolkit(UAssetEditor* InOwningAssetEditor);

protected:
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;
    virtual void BindCommands() override;

private:
    void OnCustomAction();
};
```

```cpp
// MyDemoToolkit.cpp
#include "MyDemoToolkit.h"
#include "Widgets/Text/STextBlock.h"
#include "Framework/Commands/UICommandList.h"

FMyDemoToolkit::FMyDemoToolkit(UAssetEditor* InOwningAssetEditor)
    : FMetaHumanToolkitBase(InOwningAssetEditor)
{
}

TSharedRef<SWidget> FMyDemoToolkit::GetViewportExtraContentWidget()
{
    // 创建一个简单的文本控件显示在视口底部
    return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Viewport Content")));
}

void FMyDemoToolkit::BindCommands()
{
    // 示例：绑定一个自定义命令（需要先在 CommandInfo 中定义）
    if (GetToolkitCommands().IsValid())
    {
        // 假设 FMyCustomCommands::Get().MyCustomAction 已定义
        // GetToolkitCommands()->MapAction(FMyCustomCommands::Get().MyCustomAction,
        //     FExecuteAction::CreateSP(this, &FMyDemoToolkit::OnCustomAction));
    }
}

void FMyDemoToolkit::OnCustomAction()
{
    // 自定义命令的实现逻辑
    UE_LOG(LogTemp, Log, TEXT("Custom action executed!"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心运行时库，提供基础数据类型和工具 |
| `MetaHumanPipeline` | MetaHuman 处理流水线框架，用于编排捕捉、拟合等步骤 |
| `Sequencer` | Unreal 内置的过场动画/序列器模块，用于时间轴编辑 |
| `LevelSequence` | 与 Sequencer 配套的关卡序列资产 |
| `MovieScene` | Sequencer 的底层电影场景框架 |
| `MediaAssets` | 处理媒体纹理、播放器等 |
| `CameraCalibration` | 存储和使用相机标定参数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

**积极维护中**。基于最近的 git 提交记录（2026年5月），该模块仍在持续获得功能更新和问题修复，尤其是针对身体追踪、序列器集成和渲染质量的改进。提交信息显示 Epic 仍在积极开发 MetaHuman 工具链。虽然创建时间未知，但近期的活跃更新表明它不是遗留代码。作为 MetaHuman 官方工具链的核心组成部分，它应该是稳定且推荐使用的。建议开发者跟进 Epic 官方的更新日志以获取最新变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanToolkit)
- [官方文档]() (暂无特定链接，通常包含在 MetaHuman 整体文档中)