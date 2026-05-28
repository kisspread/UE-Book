# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 身份编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、UI控件、缩略图渲染器） |
| 模块 | `MetaHumanIdentityEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentityEditor) | |

## 用途

`MetaHumanIdentityEditor` 是 MetaHuman Animator 插件的核心编辑器模块，专门用于 **管理、创建和编辑 MetaHuman 数字人的身份资产（`UMetaHumanIdentity`）**。它不是一个面向运行时的 API 模块，而是一个完整的编辑器扩展，提供了从视频或网格资产创建数字人、跟踪面部特征、拟合网格到标准模板，最终生成可动画数字人的完整工作流。其存在的根本目的是将复杂的 MetaHuman 数字人生成过程封装成一个统一的、可视化的编辑器工具。

## 使用场景

- **您正在为游戏角色创建超写实数字人**：需要从演员表演视频中捕捉并生成面部动画和外观，然后将其适配到 MetaHuman 的标准骨骼和面部绑定上。
- **您需要为虚拟主播或数字孪生应用创建可驱动的数字形象**：通过导入已有的 3D 网格或使用实时捕捉的视频流，将其转换为支持 ControlRig 和 MetaHuman Animator 的标准数字人资产。
- **您正在构建影视或虚拟制片流程**：需要一个集成的工具来管理数字角色的“身份”部分，包括中性表情、牙齿等不同姿态的网格和跟踪数据。

## 蓝图用法

此模块主要提供编辑器界面和资产操作，大部分核心逻辑由 C++ 实现并封装在 Slate UI 控件中。可供蓝图直接调用的公开节点较少，主要集中在资产操作和状态查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddPartsFromAsset` | 根据一个资产（如 StaticMesh、SkeletalMesh 或 FootageCaptureData）创建 Identity 的组成部分（Face/Body/Neutral Pose 等） | `SMetaHumanIdentityPartsEditor` |
| `GetSelectedPromotedFrame` | 返回当前在“提升帧”面板中选中的 `UMetaHumanIdentityPromotedFrame` 对象 | `SMetaHumanIdentityPromotedFramesEditor` |
| `SetIdentityPose` | 为 Promoted Frames 编辑器设置要编辑的 `UMetaHumanIdentityPose` | `SMetaHumanIdentityPromotedFramesEditor` |
| `GetIdentityPose` | 返回当前正在编辑的 `UMetaHumanIdentityPose` | `SMetaHumanIdentityPromotedFramesEditor` |
| `GetIdentity` | 返回正在编辑的 `UMetaHumanIdentity` 对象 | `SMetaHumanIdentityPartsEditor` |

### 使用示例（蓝图描述）

由于此模块主要在编辑器内通过 UI 操作，蓝图直接调用其内部 UI 函数的场景不多。一个可能的蓝图使用场景是通过编辑器工具脚本（Editor Utility Widget 或 Editor Utility Blueprint）来自动化资产处理流程：
1.  创建一个 `UMetaHumanIdentityAssetEditor` 对象。
2.  调用 `SetObjectToEdit` 指定要编辑的 `UMetaHumanIdentity` 资产。
3.  调用 `OpenEditor` 打开该资产的专用编辑器窗口。
4.  （更高级）通过获取 `FMetaHumanIdentityAssetEditorToolkit` 实例，可能访问更底层的编辑器状态和操作，但这通常需要 C++ 扩展。

## C++ 用法

此模块主要提供编辑器扩展类，用于在编辑器中处理 MetaHuman 身份资产。

### 头文件引入

```cpp
// 引入身份编辑器工具包
#include "MetaHumanIdentityAssetEditorToolkit.h"

// 引入 Parts 编辑器 UI
#include "UI/SMetaHumanIdentityPartsEditor.h"

// 引入 Promoted Frames 编辑器 UI
#include "UI/SMetaHumanIdentityPromotedFramesEditor.h"
```

### 基本用法

以下示例展示了如何以编程方式打开一个 `UMetaHumanIdentity` 资产进行编辑。这通常在编辑器工具或插件中扩展 MetaHuman 工作流时使用。

```cpp
// 文件路径: 假设的自动化脚本或插件代码
#include "MetaHumanIdentityAssetEditor.h"
#include "MetaHumanIdentity.h"

void OpenMetaHumanIdentityForEditing(UMetaHumanIdentity* InIdentity)
{
    if (!InIdentity) return;

    // 创建资产编辑器实例
    UMetaHumanIdentityAssetEditor* AssetEditor = NewObject<UMetaHumanIdentityAssetEditor>();
    AssetEditor->SetObjectToEdit(InIdentity);

    // 这会触发创建 FMetaHumanIdentityAssetEditorToolkit 并打开编辑器窗口
    AssetEditor->OpenEditor(InIdentity);
}
```

### 进阶用法

更复杂的用法涉及直接操作或扩展身份编辑器 UI。以下示例展示了如何监听 `SMetaHumanIdentityPartsEditor` 中身份部分（Part）的变化。

```cpp
// 文件路径: 假设的自定义编辑器工具代码
#include "UI/SMetaHumanIdentityPartsEditor.h"
#include "MetaHumanIdentityPart.h"

class FMyIdentityPartsMonitor
{
public:
    void StartMonitoring(const TSharedRef<SMetaHumanIdentityPartsEditor>& InPartsEditor)
    {
        // 绑定部分被添加的委托
        InPartsEditor->OnIdentityPartAddedDelegate.BindRaw(this, &FMyIdentityPartsMonitor::OnPartAdded);
        // 绑定部分被移除的委托
        InPartsEditor->OnIdentityPartRemovedDelegate.BindRaw(this, &FMyIdentityPartsMonitor::OnPartRemoved);
    }

private:
    void OnPartAdded(UMetaHumanIdentityPart* InAddedPart)
    {
        UE_LOG(LogTemp, Log, TEXT("新部分被添加到身份中: %s"), *InAddedPart->GetName());
        // 执行自定义逻辑，如验证、记录或触发其他处理
    }

    void OnPartRemoved(UMetaHumanIdentityPart* InRemovedPart)
    {
        UE_LOG(LogTemp, Log, TEXT("部分被从身份中移除: %s"), *InRemovedPart->GetName());
    }
};
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示了如何创建一个自定义编辑器工具，它继承自 MetaHuman 身份编辑器工具包，并尝试在初始化后执行一个自定义操作（仅作为演示框架）。

```cpp
// MyCustomIdentityEditorToolkit.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanIdentityAssetEditorToolkit.h"

class FMyCustomIdentityEditorToolkit : public FMetaHumanIdentityAssetEditorToolkit
{
public:
    FMyCustomIdentityEditorToolkit(UAssetEditor* InOwningAssetEditor);
    virtual ~FMyCustomIdentityEditorToolkit();

    // 重写初始化，在编辑器完全加载后执行自定义逻辑
    virtual void PostInitAssetEditor() override;

    // 添加一个自定义菜单项到工具栏
    virtual void ExtendToolBar() override;

private:
    // 自定义命令处理函数
    void HandleMyCustomAction();

    // 自定义命令信息
    TSharedPtr<FUICommandInfo> MyCustomCommand;
};
```

```cpp
// MyCustomIdentityEditorToolkit.cpp
#include "MyCustomIdentityEditorToolkit.h"
#include "MetaHumanIdentity.h"
#include "Framework/Commands/UICommandList.h"

FMyCustomIdentityEditorToolkit::FMyCustomIdentityEditorToolkit(UAssetEditor* InOwningAssetEditor)
    : FMetaHumanIdentityAssetEditorToolkit(InOwningAssetEditor)
{
    // 注册自定义命令
    MyCustomCommand = FMyCustomIdentityEditorToolkit::GetCommands().AddCommand(/* ... */);
}

FMyCustomIdentityEditorToolkit::~FMyCustomIdentityEditorToolkit()
{
}

void FMyCustomIdentityEditorToolkit::PostInitAssetEditor()
{
    // 首先调用父类初始化
    FMetaHumanIdentityAssetEditorToolkit::PostInitAssetEditor();

    // 自定义初始化：例如，检查身份资产状态并给出提示
    if (Identity && !Identity->HasFacePart())
    {
        UE_LOG(LogTemp, Warning, TEXT("当前身份资产缺少 Face 部分，请先添加。"));
    }
}

void FMyCustomIdentityEditorToolkit::ExtendToolBar()
{
    // 在调用父类添加工具栏后，我们可以继续添加更多项
    FMetaHumanIdentityAssetEditorToolkit::ExtendToolBar();

    // 获取扩展后的工具栏构建器，并添加我们的自定义按钮
    // UToolMenus::Get()->ExtendMenu("MetaHumanIdentityEditor.MainToolBar");
    // ... 添加绑定到 HandleMyCustomAction 的按钮
}

void FMyCustomIdentityEditorToolkit::HandleMyCustomAction()
{
    // 这里实现你的自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("执行自定义 MetaHuman 身份编辑器操作！"));
    // 可以访问 Identity, SelectedIdentityPose 等成员变量
}
```

## 模块依赖

使用 `MetaHumanIdentityEditor` 模块，你的项目需要依赖以下非通用模块。常见依赖如 Core, Engine, Slate 等已省略。

| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | 提供核心运行时数据结构，如 `UMetaHumanIdentity`, `UMetaHumanIdentityPart`, `UMetaHumanIdentityPose` 等 |
| `MetaHumanCaptureDataEditor` | 提供处理和可视化捕捉数据（如 FootageCaptureData）的编辑器工具 |
| `MetaHumanImageViewerEditor` | 提供图像查看和标记功能的编辑器 UI |
| `MetaHumanCore` | 提供 MetaHuman 核心技术和库的集成接口 |
| `MetaHumanToolkit` | 提供通用的 MetaHuman 编辑器工具基类（如 `FMetaHumanToolkitBase`） |
| `MetaHumanFaceContourTracker` | 提供面部轮廓跟踪的运行时算法 |
| `MetaHumanFaceFittingSolver` | 提供将跟踪结果拟合到标准模板网格的求解器 |
| `MetaHumanPipeline` | 提供用于构建处理管道的框架 |
| `UnrealEd` | 编辑器框架，用于资产编辑器、细节面板自定义等 |
| `ControlRigDeveloper` | 用于支持 ControlRig 的扩展开发和集成 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格相关的通用工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体跟踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | (MetaHuman Animator) 为现有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题 |

### 维护评价

该模块作为 MetaHuman 工作流的核心编辑器部分，处于**活跃维护**状态。
- **创建时间**：约 4 年前，与 UE5 的 MetaHuman 工具集一同推出。
- **近期更新频率**：最近一周内有多次提交，主要集中在功能增强（如身体跟踪支持、动画导出）、Bug 修复（渲染瑕疵、缓存问题）和稳定性改进。
- **维护状态**：持续由 Epic Games 团队维护，更新内容紧跟 MetaHuman 产品线的发展（如集成新的身体跟踪功能）。
- **推荐使用**：**强烈推荐**。这是使用 Unreal Engine 进行专业级 MetaHuman 数字人创建和编辑的官方且唯一完整工具链。尽管模块默认不启用（需在项目设置中手动启用 MetaHuman Animator 插件），但其功能不可或缺。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentityEditor)
- 官方文档：暂无（`.uplugin` 中 `DocsURL` 为空）。相关工作流和教程可在 Epic Games 官方 MetaHuman 文档和社区资源中找到。
- 测试用例：（此模块的测试用例通常位于 Engine/Tests/ 目录或插件内部的 Private/Tests 文件夹中，具体路径需根据源码搜索确定）