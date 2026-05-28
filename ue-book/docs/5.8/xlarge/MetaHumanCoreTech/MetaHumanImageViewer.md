# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 核心技术 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 创建和动画相关资产） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2021 年 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 MetaHuman Creator 和 MetaHuman Animator 背后的核心技术库。它提供了创建逼真数字人类所需的基础技术组件，包括：

- **人体追踪接口**：定义人体姿态追踪的抽象接口
- **捕获数据处理**：处理面部和身体的捕获数据（视频、深度图等）
- **图像查看器**：提供带有平移/缩放功能的 Slate 图像查看控件
- **处理管线核心**：MetaHuman 创建流程的管线框架

该插件是 MetaHuman 生态系统的基础依赖，被 MetaHuman Creator（云端创建工具）和 MetaHuman Animator（本地面部动画工具）共同使用。

## 使用场景

- 你在开发 MetaHuman Animator 插件 → 需要依赖此插件的核心追踪和管线功能
- 你需要处理面部捕获数据（单目/多目视频） → 使用 MetaHumanCaptureData 模块
- 你需要在编辑器中显示带交互功能的图像预览 → 使用 MetaHumanImageViewer 模块
- 你在开发自定义的人体追踪解决方案 → 实现 MetaHumanBodyTrackerInterface 接口

## 蓝图用法

此插件主要提供 C++ 运行时功能，BlueprintCallable API 较少。核心功能通过 C++ 接口提供。

### 核心节点

由于 MetaHumanCoreTech 主要是底层技术库，大部分功能通过 C++ 接口访问。编辑器相关的 UI 功能（如图像查看器）仅在编辑器环境中使用。

## C++ 用法

### 基本用法 - MetaHumanImageViewer 模块

MetaHumanImageViewer 提供了一个带有交互功能的 Slate 图像查看控件，支持平移和缩放。

#### 头文件引入

```cpp
#include "SMetaHumanImageViewer.h"
```

#### 在 Slate 中创建图像查看器

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanImageViewer/Public/SMetaHumanImageViewer.h

// 创建图像查看器控件
TSharedRef<SMetaHumanImageViewer> ImageViewer = SNew(SMetaHumanImageViewer)
    .Image(MyBrushAttribute)
    .CommandList(MyCommandList);

// 监听视图变化（平移/缩放）
ImageViewer->OnViewChanged.AddLambda([](const FBox2f& NewUVRange)
{
    // 处理视图范围变化
    UE_LOG(LogTemp, Log, TEXT("View changed: Min=(%f,%f), Max=(%f,%f)"),
        NewUVRange.Min.X, NewUVRange.Min.Y,
        NewUVRange.Max.X, NewUVRange.Max.Y);
});

// 重置视图到默认状态
ImageViewer->ResetView();

// 控制空白区域绘制
ImageViewer->SetDrawBlanking(false);
```

#### 自定义鼠标交互

```cpp
// SMetaHumanImageViewer 提供了可重写的鼠标处理函数
class MyCustomImageViewer : public SMetaHumanImageViewer
{
protected:
    virtual FReply HandleMouseButtonDown(
        const FGeometry& InGeometry,
        const FVector2f& InLocalMouse,
        const FKey& InEffectingButton) override
    {
        // 自定义鼠标按下逻辑
        if (InEffectingButton == EKeys::RightMouseButton)
        {
            // 自定义右键行为
        }
        return SMetaHumanImageViewer::HandleMouseButtonDown(InGeometry, InLocalMouse, InEffectingButton);
    }
};
```

## Demo 示例

### MetaHumanImageViewer 基本用法

```cpp
// MyImagePreviewWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMetaHumanImageViewer;

class SMyImagePreviewWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyImagePreviewWidget) {}
        SLATE_ATTRIBUTE(const FSlateBrush*, PreviewImage)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SMetaHumanImageViewer> ImageViewer;
    void OnViewChanged(const FBox2f& NewUVRange);
};
```

```cpp
// MyImagePreviewWidget.cpp
#include "MyImagePreviewWidget.h"
#include "SMetaHumanImageViewer.h"

void SMyImagePreviewWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SAssignNew(ImageViewer, SMetaHumanImageViewer)
            .Image(InArgs._PreviewImage)
            .CommandList(nullptr)
    ];

    ImageViewer->OnViewChanged.AddSP(this, &SMyImagePreviewWidget::OnViewChanged);
}

void SMyImagePreviewWidget::OnViewChanged(const FBox2f& NewUVRange)
{
    // 更新其他 UI 元素或处理逻辑
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenCV` | 计算机视觉库，用于图像处理 |
| `OpenCVHelper` | OpenCV 的 UE5 封装辅助模块 |
| `DirectoryWatcher` | 文件系统监控，用于捕获数据热加载 |
| `OnlineSubsystem` | 在线子系统（可能用于 MetaHuman Creator 云端通信） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman Titan 引擎更新至 v9.0.8 版本 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman Titan 引擎更新至 v9.0.7 版本 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | MetaHuman Titan 引擎更新至 v9.0.6 版本 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 人体追踪器新增脚部锁定开关功能 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复 MetaHuman Animator 在 MHC 组装时的崩溃问题 |

### 维护评价

**🟢 活跃维护**

MetaHumanCoreTech 是 Epic Games 官方维护的核心插件，处于**极度活跃**的维护状态：

- **更新频率**：每周多次提交，最近一周内有 5 次更新
- **版本迭代**：Titan 引擎持续更新（v9.0.6 → v9.0.8），表明底层技术在持续优化
- **功能扩展**：新增身体追踪功能（脚部锁定），表明仍在积极开发新特性
- **Bug 修复**：及时修复关键崩溃问题

**注意事项**：
- 此插件默认未启用（`EnabledByDefault: false`），需要配合 MetaHuman Creator 或 MetaHuman Animator 插件使用
- 作为底层技术库，不建议单独使用，应作为其他 MetaHuman 插件的依赖

**推荐使用**：✅ 如果你在使用 MetaHuman 技术栈，此插件是必需的核心依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-in-unreal-engine/)
- [MetaHuman Creator](https://metahuman.unrealengine.com/)