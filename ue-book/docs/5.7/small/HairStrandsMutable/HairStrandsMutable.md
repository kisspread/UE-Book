# Mutable Groom Extensions

> Adds Mutable functionality to work with Grooms from the HairStrands plugin

| 属性 | 值 |
|---|---|
| 中文名 | 发型可变扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairStrandsMutable` (Runtime), `HairStrandsMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable) | |

## 用途

该插件为 **Mutable（可变）** 系统提供发型（Groom）扩展，允许用户将 HairStrands 插件中的 `UGroomAsset`、`UGroomCache`、`UGroomBindingAsset` 等资源集成到 Customizable Object（可定制对象）图形中。通过定义 `FGroomPinData` 结构体，该插件在 Mutable 工程图中新增了一个专门的头像（Groom）引脚类型，使得在 Mutable 编辑器中能够像操作普通 mesh 一样配置并动态生成发型组件。

## 使用场景

- 你在制作一个使用 Mutable 实现角色自定义的项目，需要为角色附加发型（如头发、胡须等）并支持运行时切换或变形。
- 你需要让 HairStrands 插件提供的物理模拟发型与 Mutable 的可变系统协同工作，自动将发型绑定到可变网格体上。

## 蓝图用法

该插件主要是通过 Mutable 的系统自动集成，不提供独立的蓝图可调用节点。但在 Mutable 编辑器中，会新增一个引脚类型 `Groom`（`FGroomPinData`），用户可以通过 Mutable 的“自定义对象扩展（Customizable Object Extension）”功能在蓝图或 Mutable 工程图中配置发型参数。

### 核心数据结构

| 结构体 | 说明 |
|---|---|
| `FGroomPinData` | 表示单个发型实例的引脚数据，包含附着组件、发型资产、缓存、绑定资产、物理资产、组件命名和材质覆盖等属性。 |
| `FGroomInstanceData` | 包含一组 `FGroomPinData` 的数组，用于在运行时传递所有发型实例。 |

### 使用示例（蓝图描述）

1. 在 Mutable 编辑器中，打开一个 Customizable Object 的节点图。
2. 添加一个“扩展引脚（Extension Pin）”节点（由插件自动提供），引脚类型选择 `Groom`。
3. 连接该引脚到目标 mesh 组件节点（如 `MeshObject` 的附加引脚）。
4. 通过 Mutable 的实例化系统，在蓝图或运行时设置每个实例的 `FGroomPinData` 属性（如 `GroomAsset`、`ComponentName` 等）。

## C++ 用法

### 头文件引入

```cpp
#include "HairStrandsMutableExtension.h"
```

### 基本用法

插件提供 `UHairStrandsMutableExtension` 类，继承自 `UCustomizableObjectExtension`，用于注册自定义引脚类型并处理实例数据生成。

**示例：注册并使用 Groom 引脚**（源自源码注释）

```cpp
// 创建一个 CustomizableObjectInstance
UCustomizableObjectInstance* Instance = ...;

// 设置 Groom 数据（用法类似于其他 Mutable 扩展）
// 此处仅示意，实际通过实例的 Update 接口传递
UHairStrandsMutableExtension* Extension = ...;
Extension->GetPinTypes(); // 返回 [FName("Groom")]
// 在实例化时自动调用 GenerateExtensionInstanceData 生成 FGroomInstanceData
```

### 进阶用法

通过覆盖基类方法实现自定义行为：

- `GetPinTypes()` – 返回该扩展提供的引脚类型列表，仅包含 `Groom`。
- `GetAdditionalObjectNodePins()` – 返回对象节点上额外的输入引脚，用于连接 Groom 输入。
- `GenerateExtensionInstanceData()` – 根据输入引脚数据生成 `FGroomInstanceData`（内含 `FGroomPinData` 数组）。
- `OnCustomizableObjectInstanceUsageUpdated()` – 当 Mutable 实例的用法更新时被调用，用于同步发型组件（如创建 `UGroomComponent`）。
- `OnCustomizableObjectInstanceUsageDiscarded()` – 当用法被丢弃时清理相关组件。

典型调用流程（在 Mutable 系统内部自动触发）：
```cpp
// 1. 用户通过 Mutable 实例设置 Groom 引脚数据
// 2. 扩展在实例编译时调用 GenerateExtensionInstanceData()
// 3. 运行时调用 OnCustomizableObjectInstanceUsageUpdated() 创建或更新 GroomComponent
// 4. 销毁时调用 OnCustomizableObjectInstanceUsageDiscarded() 清理组件
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何在 Mutable 实例中获取 Groom 引脚类型并创建扩展实例（假设已有 CustomizableObject 实例）。

**MyCustomizableActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HairStrandsMutableExtension.h"
#include "MyCustomizableActor.generated.h"

UCLASS()
class AMyCustomizableActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mutable")
    UCustomizableObjectInstance* CustomizableInstance;

    void SetupGroomExtension()
    {
        if (!CustomizableInstance)
        {
            return;
        }

        // 获取 Mutable 扩展实例（插件自动创建）
        UCustomizableObjectExtension* Extension = ...; // 通过 Instance 获取
        if (Extension && Extension->IsA<UHairStrandsMutableExtension>())
        {
            UHairStrandsMutableExtension* HairExtension = Cast<UHairStrandsMutableExtension>(Extension);
            TArray<FCustomizableObjectPinType> PinTypes = HairExtension->GetPinTypes();
            // 确认存在 Groom 引脚类型
            ensure(PinTypes.Num() > 0 && PinTypes[0].PinName == UHairStrandsMutableExtension::GroomPinType);
        }
    }
};
```

**MyCustomizableActor.cpp**
```cpp
#include "MyCustomizableActor.h"
```

> 注：实际使用时需要根据 Mutable 实例的接口获取扩展对象，此处仅示意。

## 模块依赖

省略常见依赖（Core、Engine 等），仅列出该插件特有的依赖。

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供发型（Groom）核心资源类型（`UGroomAsset`、`UGroomComponent` 等） |
| `Mutable` (CustomizableObject) | 提供 Mutable 可定制对象系统框架及扩展接口基类（`UCustomizableObjectExtension`） |

## 维护状态

### 近期更新

- 2025-09-01 75e4adbd [Mutable] Change namespace name
- 2025-08-29 24228d19 [mutable] Changed friendly name to the MutableDataflow and HairStrandsMutable experimental plugins.
- 2025-08-26 1dbf0316 [Mutable] Add component naming support for spawned groom components
- 2025-06-20 1ec52cfd [Mutable] Allow load and recompile of the CustomizableObject model when in-game mode.
- 2025-01-29 ea8756da [Mutable] Convert ModelResources to UObject.

### 维护评价

该插件创建于 2025 年初，至今（2025 年 10 月）仍在积极维护，最近一次更新在 2025 年 9 月。更新内容涉及命名空间、友好名称调整、组件命名支持等，属于实验性插件（`IsExperimentalVersion=true`），功能在逐步完善。推荐在开发环境中使用，但生产部署需谨慎，关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable/Source)（本插件测试文件位于源码目录内）