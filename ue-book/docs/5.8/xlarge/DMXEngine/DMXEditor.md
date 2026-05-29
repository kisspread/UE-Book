# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 中文名 | DMX 引擎 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (Runtime), `DMXEditor` (Runtime), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMXEngine 是 UE5 虚拟制片管线中用于管理 DMX 灯光控制设备的核心插件。它解决的核心问题是：在虚拟制片环境中，如何标准化地定义、编辑、通信和录制来自 DMX 设备（如电脑摇头灯、LED 面板等）的灯光控制数据。

该插件的存在基于以下需求：
1.  **标准化定义**：提供统一的资产类型（DMX Library, Fixture Type, Fixture Patch）来定义 DMX 设备的能力（通道、模式、功能）。
2.  **可视化编辑**：通过专门的编辑器界面，让用户能够直观地配置设备属性、分配通道和管理灯光预设。
3.  **运行时通信**：提供蓝图和C++接口，用于在运行时发送和接收DMX数据，实现与物理灯光设备的实时交互。
4.  **序列集成**：与 Sequencer 深度集成，允许录制和播放DMX数据动画，实现灯光效果的精确重现。
5.  **行业标准支持**：支持导入导出 GDTF（通用设备类型格式）和 MVR（虚拟现实场景）文件，便于与其他灯光软件和设计师工作流对接。

## 使用场景

-   **虚拟制片灯光控制**：你在使用 LED Volume 或其他 LED 墙进行拍摄时，需要同步控制现场实体灯光与虚拟场景。使用 DMXEngine 管理灯光预设，并通过 Sequencer 录制和回放精确的灯光效果。
-   **大型活动灯光编程与测试**：你在为一场演出编程复杂的灯光秀，希望在 UE5 中预先模拟和测试灯光效果，避免现场调试风险。使用 DMXEngine 创建灯光库，通过蓝图或控制台工具发送控制信号进行预览。
-   **DMX 设备集成开发**：你正在开发一个需要集成 DMX 灯光的虚拟体验或游戏。使用 DMXEngine 管理设备通信，通过蓝图节点“Set Fixture Patch Channel Value”来动态控制场景中的灯光。
-   **从外部软件迁移**：你使用如 Vectorworks, Capture 等专业灯光设计软件完成了灯光设计，希望将其导入 UE5。使用 DMXEngine 导入 MVR 文件，快速在 UE5 中重建灯光场景。

## 蓝图用法

该插件的核心蓝图功能围绕 `UDMXSubsystem` 和 `UDMXLibrary` 展开。以下为常用的核心节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get DMX Library` | 获取指定名称的 DMX 库资产 | `UDMXSubsystem` |
| `Send DMX` | 向指定的 Fixture Patch 发送完整的通道值数据 | `UDMXSubsystem` |
| `Set Fixture Patch Channel Value` | 设置指定 Fixture Patch 单个通道的值 | `UDMXSubsystem` |
| `Get Fixture Patch Channel Value` | 获取指定 Fixture Patch 单个通道的当前值 | `UDMXSubsystem` |
| `Create DMX Fixture Patch` | 在指定的 DMX 库中创建一个新的 Fixture Patch | `UDMXLibrary` |
| `Get Fixture Patches` | 获取 DMX 库中所有的 Fixture Patch 列表 | `UDMXLibrary` |
| `Import GDTF From File` | 从文件导入一个 GDTF 灯具描述文件到 DMX 库 | `UDMXLibrary` |
| `Export Library To MVR` | 将整个 DMX 库导出为 MVR 文件 | `UDMXLibrary` |

### 使用示例（蓝图描述）

**示例1：在运行时控制灯光**
1.  获取 `DMX Subsystem`。
2.  从内容浏览器中引用一个 `DMX Library` 资产。
3.  调用 `Get Fixture Patches` 节点，获取目标 `Fixture Patch` 的引用。
4.  使用 `Set Fixture Patch Channel Value` 节点，指定 `Fixture Patch`、通道名称（如“Intensity”）和目标值（0.0 到 1.0）。
5.  物理灯光设备将根据设定的值改变亮度。

**示例2：录制DMX灯光动画**
1.  在 Sequencer 中添加一个 `Take Recorder` 轨道。
2.  在 `Take Recorder` 的设置面板中，添加 `DMX Library` 源。
3.  选择要录制的 `Fixture Patch`。
4.  点击录制按钮。此时，所有通过选定 `Fixture Patch` 接收到的 DMX 数据都会被录制到 Sequencer 轨道中。
5.  停止录制后，可以在 Sequencer 中回放和编辑这段灯光动画。

## C++ 用法

该插件的主要 C++ API 暴露在 `DMXEditor`、`DMXRuntime` 和 `DMXBlueprintGraph` 模块中。以下示例展示了如何以编程方式与 DMX 编辑器交互。

### 头文件引入

```cpp
// 用于访问 DMX 编辑器功能
#include "DMXEditorModule.h"
// 用于操作 DMX 库和实体
#include "DMXLibrary.h"
#include "DMXEntityFixturePatch.h"
```

### 基本用法

**获取 DMX 编辑器模块实例并创建编辑器** (来源: `Public/DMXEditorModule.h`)
```cpp
// 获取 DMX 编辑器模块
FDMXEditorModule& DMXEditorModule = FDMXEditorModule::Get();

// 假设已有一个 UDMXLibrary* DMXLibrary 指针
UDMXLibrary* MyDMXLibrary = /* ... */;

// 在独立编辑器模式中打开该 DMX 库的编辑器
TSharedRef<FDMXEditor> DMXEditor = DMXEditorModule.CreateEditor(
    EToolkitMode::Standalone,
    nullptr, // 无主窗口宿主
    MyDMXLibrary
);

// DMXEditor 现在是活动的，可以调用其公共方法
// 例如，切换到 Fixture Patch 编辑选项卡
DMXEditor->InvokeEditorTabFromEntityType(UDMXEntityFixturePatch::StaticClass());
```

### 进阶用法

**通过 DMX Editor 选择并操作实体** (综合 `Public/DMXEditor.h` 和 `DMXEditorUtils.h` 的使用模式)
```cpp
// 续前例，DMXEditor 已创建
// 获取 Fixture Patch 编辑器中的共享数据
TSharedPtr<FDMXFixturePatchSharedData> PatchSharedData = DMXEditor->GetFixturePatchSharedData();

// 获取当前在编辑器中选中的 Fixture Patches
TArray<UDMXEntityFixturePatch*> SelectedPatches;
// ... (通过编辑器交互获取选中项)

// 使用工具类重命名一个实体
UDMXEntity* EntityToRename = SelectedPatches[0];
FText Reason;
FString NewName = TEXT("MyRenamedPatch");
if (FDMXEditorUtils::ValidateEntityName(NewName, MyDMXLibrary, UDMXEntityFixturePatch::StaticClass(), Reason))
{
    FDMXEditorUtils::RenameEntity(MyDMXLibrary, EntityToRename, NewName);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Cannot rename: %s"), *Reason.ToString());
}

// 将选中的 Fixture Patches 自动分配到可用通道
UE::DMXEditor::AutoAssign::FAutoAssignUtility::AutoAssign(
    UE::DMXEditor::AutoAssign::EAutoAssignMode::FirstReachableUniverse,
    DMXEditor,
    SelectedPatches
);
```

## Demo 示例

以下是一个最小化 C++ 示例，展示如何通过编程方式创建一个 DMX 编辑器实例并触发实体操作。

**MyDMXActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyDMXActor.generated.h"

class UDMXLibrary;
class FDMXEditor;

UCLASS()
class AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

    UPROPERTY(EditAnywhere, Category = "DMX")
    TObjectPtr<UDMXLibrary> MyDMXLibrary;

    UFUNCTION(BlueprintCallable, Category = "DMX")
    void OpenDMXEditorAndAddPatch();

private:
    TSharedPtr<FDMXEditor> ActiveDMXEditor;
};
```

**MyDMXActor.cpp**
```cpp
#include "MyDMXActor.h"
#include "DMXEditorModule.h"
#include "DMXLibrary.h"
#include "DMXEntityFixturePatch.h"

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDMXActor::OpenDMXEditorAndAddPatch()
{
    if (!MyDMXLibrary)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyDMXLibrary is not set."));
        return;
    }

    // 获取并创建编辑器实例
    FDMXEditorModule& EditorModule = FDMXEditorModule::Get();
    ActiveDMXEditor = EditorModule.CreateEditor(
        EToolkitMode::Standalone,
        nullptr,
        MyDMXLibrary
    );

    // 延迟一帧执行，以确保编辑器初始化完成
    GetWorldTimerManager().SetTimerForNextTick([this]()
    {
        if (ActiveDMXEditor.IsValid())
        {
            // 切换到 Fixture Patch 选项卡
            ActiveDMXEditor->InvokeEditorTabFromEntityType(UDMXEntityFixturePatch::StaticClass());

            // 程序化地执行“添加新 Fixture Patch”的命令
            // 这会触发编辑器内部的逻辑，弹出创建向导
            // 注意：直接调用需要访问编辑器内部命令，此处为示意。
            // 更推荐的方式是通过蓝图或UI交互。
            UE_LOG(LogTemp, Log, TEXT("DMX Editor opened. Add a new Fixture Patch via the UI."));
        }
    });
}
```

## 模块依赖

要在你的项目或插件中使用 DMXEngine 的功能，你的模块需要依赖以下特定模块（除了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `DMXRuntime` | 提供 DMX 库、实体、端口、子系统等核心运行时类和通信逻辑。 |
| `DMXProtocol` | 提供底层的 DMX 协议实现（如 sACN, Art-Net）支持。 |
| `MVR` | 处理 MVR（My Virtual Rig）文件的导入导出和解析。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `96d3b290` | DMX - Fix a crash when trying to edit a sequence with a fixture patch that no longer contains a mode | 修复了当编辑一个已不再包含模式的 Fixture Patch 的序列时发生的崩溃问题。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将多种虚拟制片资产移动到了不同的资产分类下，并进行了迁移。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 调用迁移到 UE_LOGF 宏。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 改进了包保存状态检查相关的代码。 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now ... | 移除了受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5` 保护的头文件包含，并删除了现在多余的头文件。 |

### 维护评价

-   **创建时间**：2020年9月，已有约5年历史。
-   **近期更新频率**：截至2026年5月仍有活跃更新，且修复了关键的运行时崩溃问题，表明该插件仍在积极维护中。
-   **维护状态**：**活跃维护**。作为 Epic Games 官方维护的虚拟制片核心模块之一，它会随着 UE5 版本的迭代持续更新。
-   **已知问题/限制**：从 git 记录看，近期更新集中在修复 bug、代码清理和适应引擎 API 变更（如 UE_LOGF），暂无重大功能缺陷报告。其复杂性（341个源文件）意味着学习曲线较陡。
-   **推荐使用**：**强烈推荐**在所有需要集成 DMX 灯光控制的虚拟制片项目中使用。它是 UE5 中与专业灯光设备交互的标准方案，提供了从设计到回放的完整工作流。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
-   [官方文档]() (待补充， 插件元数据中 `DocsURL` 为空)