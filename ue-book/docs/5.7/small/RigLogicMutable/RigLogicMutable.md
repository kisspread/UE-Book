# RigLogic Extensions For Mutable

> Adds Mutable functionality to work with RigLogic DNA

| 属性 | 值 |
|---|---|
| 中文名 | 可变体-DNA扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicMutable` (Runtime), `RigLogicMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable) | |

## 用途

本插件桥接了 **Mutable（可变对象系统）** 与 **RigLogic（DNA 面部动画）** 两个子系统，允许用户在可变对象图中直接引用并传递 RigLogic DNA 资产。  
通常，RigLogic 用于驱动面部表情（BlendShape 或骨骼动画），但 DNA 资产需要在运行时动态绑定到网格体上。通过 Mutable 的扩展能力，可将 DNA 资产作为引脚（Pin）数据传入可变对象图，最终在生成的骨骼网格体上自动应用 DNA。

**核心价值**：解决“可变角色捏脸 + RigLogic 面部动画”的组合需求，无需手动在后端绑定 DNA。

## 使用场景

- **捏脸系统 + 面部动画**  
  使用 Mutable 生成不同外观的角色（如发型、肤色、服饰），同时需要 RigLogic 根据 DNA 数据驱动面部表情（如眨眼、张嘴）。此插件允许将 DNA 资产通过 Mutable 图传递，使最终生成的网格体自动与 DNA 关联。

- **动态更换 DNA**  
  在运行时根据玩家选择的预设或自定义捏脸参数，修改传入的 DNA 资产（通过 `FDNAPinData` 结构体），从而改变面部动画效果。

## 蓝图用法

本插件未暴露直接可调用的蓝图函数（`UFUNCTION(BlueprintCallable)`）。主要交互方式是在 **Mutable 图编辑器** 中通过 **自定义引脚类型** 间接使用。

### 核心概念

| 概念 | 说明 | 对应类 |
|---|---|---|
| DNA Pin 数据类型 | 一个特殊的结构体，用于在 Mutable 图节点之间传递 DNA 资产引用（所有权唯一，不支持拷贝） | `FDNAPinData` |
| 自定义引脚 | 在 Mutable 的可变对象扩展中注册的引脚类型，允许图为节点提供 DNA 数据输入 | `URigLogicMutableExtension::DNAPinType` |
| DNA 基础节点引脚 | 在 Mutable 图根节点上添加的额外引脚，用于接收全局 DNA 资产 | `URigLogicMutableExtension::DNABaseNodePinName` |

### 在 Mutable 图中使用 DNA 引脚

1. 确保已为项目启用了 `RigLogicMutable` 插件（在插件管理器中手动启用）。
2. 打开一个 Mutable 图资产（`CustomizableObject`）。
3. 在图的属性中，可以看到新增的 **DNA Base** 引脚（名称为 `DNABase`）。
4. 创建一个 **常量引脚** 节点，类型选择 `DNAPinData`，并设置其 `ComponentName` 和 DNA 资产引用。
5. 将该节点的输出连接到图的 `DNABase` 输入引脚。
6. 当该 Mutable 对象被实例化并生成骨骼网格体时，插件会自动将 DNA 关联到对应的骨骼网格体组件上。

> **注意**：`FDNAPinData` 结构体不允许拷贝，在蓝图中使用时应注意所有权（通常由 Mutable 系统管理）。

## C++ 用法

### 头文件引入

```cpp
#include "RigLogicMutableExtension.h"
```

### 基本用法

#### 创建并传递 DNA Pin 数据

```cpp
// 假设已有 UDNAAsset* 对象 (SourceDNA)
UDNAAsset* SourceDNA = /* 从某处获取 */;
UObject* Outer = GetTransientPackage();

// 1. 创建 FDNAPinData 实例
FDNAPinData PinData;
PinData.ComponentName = FName("FaceMesh");  // 指定目标组件名称

// 2. 设置 DNA 资产（转移所有权）
PinData.SetDNAAsset(SourceDNA);

// 3. 若需要复制 DNA 资产（例如用于多个实例），使用 URigLogicMutableExtension::CopyDNAAsset
UDNAAsset* CopiedDNA = URigLogicMutableExtension::CopyDNAAsset(SourceDNA, Outer);
FDNAPinData AnotherPinData;
AnotherPinData.SetDNAAsset(CopiedDNA);
```

#### 在 C++ 中集成到 Mutable 实例化流程

通常 Mutable 实例化由 `UCustomizableObjectInstance` 管理。你可以在实例化前将 DNA Pin 数据注入到 `FInputPinDataContainer` 中。例如：

```cpp
// 创建实例对象
UCustomizableObjectInstance* Instance = MutableObj->CreateInstance();

// 获取根节点的输入引脚数据数组
TArray<FInputPinDataContainer>& InputPinData = Instance->GetInputPinData();

// 查找或添加 DNABase 引脚数据
// 注意：具体索引需根据 Mutable Object 定义获取，此处仅为示例
FInputPinDataContainer& DNAPinContainer = InputPinData.AddDefaulted_GetRef();
DNAPinContainer.PinName = URigLogicMutableExtension::DNABaseNodePinName; // "DNABase"

// 将我们的 FDNAPinData 以 FInstancedStruct 形式存储
FInstancedStruct PinStruct;
PinStruct.InitializeAs<FDNAPinData>();
PinStruct.GetMutable<FDNAPinData>().SetDNAAsset(MyDNAAsset);
DNAPinContainer.Data = PinStruct;
```

### 进阶用法

#### 自定义扩展节点的引脚处理

如果实现了自己的 `UCustomizableObjectExtension` 派生类，可通过重载 `GetPinTypes`、`GetAdditionalObjectNodePins` 和 `OnSkeletalMeshCreated` 来定义新的 DNA 引脚行为。可参考 `URigLogicMutableExtension` 的实现。

#### 编辑器内部：迁移 DNA 资产所有权

当在编辑器中进行复制（Ctrl+W）等操作时，`FDNAPinData` 的拷贝被禁用。插件通过 `MovePrivateReferencesToContainer` 方法确保 DNA 资产的所有权正确转移到新的容器对象中。自定义扩展也需遵循此模式。

## Demo 示例

以下是一个最小 C++ 示例，展示如何从某处获取 DNA 资产并在运行时为 Mutable 实例设置 DNA 引脚。

**FMyGameModule.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    void SetupDNAForMutableInstance(class UCustomizableObjectInstance* Instance, class UDNAAsset* DNA);
};
```

**FMyGameModule.cpp**

```cpp
#include "FMyGameModule.h"
#include "RigLogicMutableExtension.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/InputPinDataContainer.h"

void FMyGameModule::SetupDNAForMutableInstance(UCustomizableObjectInstance* Instance, UDNAAsset* DNA)
{
    if (!Instance || !DNA) return;

    // 获取实例的输入引脚数据
    TArray<FInputPinDataContainer>& InputPinData = Instance->GetInputPinData();

    // 查找是否已有 DNABase 引脚，若没有则添加
    FInputPinDataContainer* DNAContainer = InputPinData.FindByPredicate(
        [](const FInputPinDataContainer& C) { return C.PinName == URigLogicMutableExtension::DNABaseNodePinName; }
    );
    if (!DNAContainer)
    {
        DNAContainer = &InputPinData.AddDefaulted_GetRef();
        DNAContainer->PinName = URigLogicMutableExtension::DNABaseNodePinName;
    }

    // 创建 FDNAPinData 并设置（注意所有权转移）
    FDNAPinData PinData;
    PinData.ComponentName = FName("Face"); // 匹配骨骼网格体组件名称
    PinData.SetDNAAsset(DNA);  // 现在 DNA 归这个 PinData 所有，原调用者不再持有

    // 打包到 FInstancedStruct
    FInstancedStruct Struct;
    Struct.InitializeAs<FDNAPinData>();
    *Struct.GetMutablePtr<FDNAPinData>() = MoveTemp(PinData); // 再次转移所有权

    // 设置到容器
    DNAContainer->Data = Struct;
}
```

> **注意**：本示例假设 `GetInputPinData()` 返回可写引用且索引存在。实际使用请参考 Mutable API 的最新文档。此示例仅在运行时调用一次，避免多次设置同一个 DNA 导致所有权混乱。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogicModule` | 核心 RigLogic 功能：DNA 资产加载、解算 |
| `MutableRuntime` | 可变对象系统运行时（`CustomizableObject`、`Extension` 等） |
| `CustomizableObject` | Mutable 的核心 API（`UCustomizableObjectExtension` 基类） |

> 此外，`RigLogicMutableEditor` 额外依赖 `UnrealEd`、`MutableEditor` 等编辑器模块。

## 维护状态

### 近期更新

- 2025-09-01 `75e4adb` — [Mutable] Change namespace name（命名空间变更）
- 2025-06-20 `1ec52cf` — [Mutable] Allow load and recompile of the CustomizableObject model when in-game mode.
- 2025-02-06 `41fd6b9` — [mutable] Fix compilation for plugin after removal of AddParticipatingObjects method.
- 2025-01-29 `ea8756d` — [Mutable] Convert ModelResources to UObject.
- 2024-12-09 `17fd03f` — [RigLogicMutable] Fixed Game crash when generating a SKM with DNA.（首个功能性修复）

### 维护评价

- **创建时间**：2024-12-09，距今约 1 年。
- **近期更新**：最近一次实质性更新在 2025-09（命名空间调整），后续多为配合 Mutable 系统变更的适配性修改。
- **活跃度**：维护跟随 Mutable 系统同步，但插件本身功能改动很少，属于“维护中”但非高频迭代。
- **已知问题**：由于是实验性插件，API 可能随 Mutable 版本变化；`FDNAPinData` 禁止拷贝，需谨慎处理所有权。
- **推荐使用**：若项目同时使用 Mutable 和 RigLogic，推荐启用此插件以简化集成流程。但请注意其实验性状态，建议在开发阶段充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable)
- [官方文档（无）](https://dev.epicgames.com/documentation/en-us/unreal-engine/riglogic-face-animation) （通用 RigLogic 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable/Tests)（如存在）