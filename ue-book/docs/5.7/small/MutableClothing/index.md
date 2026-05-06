# Mutable Clothing

> Adds Mutable functionality to work with clothing

| 属性 | 值 |
|---|---|
| 中文名 | Mutable 服装扩展 |
| 分类 | Mutable |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableClothing` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutableClothing) | |

---

## 用途

该插件是 **Mutable**（Customizable Object）系统与 Unreal Engine 内置服装系统（`ClothingSimulation`）之间的桥梁。  
它提供关键功能：

- **更新服装模拟 LOD**：将 Mutable 生成的服装网格数据（如顶点、权重）注入到标准服装资产（`UClothingAssetCommon`）中，使其能够参与布料模拟。
- **修复 LOD 过渡映射**：当 Mutable 动态修改服装网格拓扑时，确保 LOD 之间的过渡蒙皮权重正确传递，避免穿模或撕裂。

简单来说，若你使用 **Mutable** 实现动态换装，并且希望服装具有物理布料效果（如飘动），就需要此插件将两者集成。

---

## 使用场景

- **动态换装 + 布料模拟**：角色通过 Mutable 实时切换不同服装，且每件服装需具备独立的布料物理（如裙摆、披风）。
- **高自定义服装系统**：玩家可在游戏内调整服装形状、材质，同时保留布料的真实受力表现。
- **MMO / 大世界**：大量角色穿着由 Mutable 生成的服装，需要高效地将服装数据传递给布料系统，同时支持 LOD 过渡。

---

## 蓝图用法

该插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。所有功能仅在 C++ 层面通过 `IMutableClothingModule` 接口提供，供 Mutable 系统内部调用。

> 注意：间接使用时，你仍可以在蓝图节点中找到与服装模拟相关的常规节点（如 `Set Clothing Sim LOD`），但这些节点不依赖本插件。本插件仅作为底层数据管线的一部分自动工作。

---

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/Plugins/IMutableClothingModule.h"
#include "MutableClothingModule.h"   // 可选，用于访问 LogCategory
```

### 基本用法

**1. 获取模块实例**

```cpp
IMutableClothingModule* ClothingModule = FModuleManager::LoadModulePtr<IMutableClothingModule>("MutableClothing");
if (ClothingModule)
{
    // 可调用 UpdateClothSimulationLOD 等
}
```

**2. 更新服装模拟 LOD**

通常由 Mutable 系统在生成服装网格后自动调用，但也可手动触发：

```cpp
// 假设有一个 UClothingAssetCommon* ClothingAsset 和一个 InSimulationLODIndex
TArray<TArrayView<FMeshToMeshVertData>> AttachedLODsRenderData; // 填充 LOD 间的映射数据

bool bSuccess = ClothingModule->UpdateClothSimulationLOD(
    InSimulationLODIndex,
    *ClothingAsset,
    AttachedLODsRenderData
);
// bSuccess 为 true 表示更新成功
```

**3. 修复 LOD 过渡映射**

当服装资产内部 LOD 层级发生变化时（如 Mutable 增删了某个 LOD），需要调用此函数重新计算过渡映射：

```cpp
ClothingModule->FixLODTransitionMappings(InSimulationLODIndex, *ClothingAsset);
```

> 来源文件：`Engine/Plugins/Experimental/MutableClothing/Source/MutableClothing/Private/MutableClothingModule.cpp`（未提供，但根据接口签名推断）。

### 进阶用法

结合 Mutable 的 `UCustomizableObjectInstance` 使用：

```cpp
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/Plugins/IMutableClothingModule.h"

// 假设已创建 CustomizableObjectInstance 并生成了实例
UCustomizableObjectInstance* Instance = ...;
UClothingAssetCommon* ClothingAsset = 获取服装资产的逻辑(); // 通常从实例的 MeshComponents 中读取

if (IMutableClothingModule* ClothingModule = FModuleManager::LoadModulePtr<IMutableClothingModule>("MutableClothing"))
{
    // 遍历所有模拟 LOD
    for (int32 LODIndex = 0; LODIndex < ClothingAsset->LodData.Num(); ++LODIndex)
    {
        ClothingModule->UpdateClothSimulationLOD(LODIndex, *ClothingAsset, ClothingAsset->LodData[LODIndex].TransitionUpSkinData);
        ClothingModule->FixLODTransitionMappings(LODIndex, *ClothingAsset);
    }
}
```

---

## Demo 示例

以下是一个最小 C++ 示例，演示如何在游戏模块启动时强制更新一个已有的服装资产 LOD。

### MyClothingTest.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyClothingTest.generated.h"

UCLASS()
class UMyClothingTest : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION()
    void ForceUpdateClothingLOD(UClothingAssetCommon* ClothingAsset, int32 LODIndex);
};
```

### MyClothingTest.cpp

```cpp
#include "MyClothingTest.h"
#include "MuCO/Plugins/IMutableClothingModule.h"
#include "ClothingAssetCommon.h"
#include "Modules/ModuleManager.h"

void UMyClothingTest::ForceUpdateClothingLOD(UClothingAssetCommon* ClothingAsset, int32 LODIndex)
{
    if (!ClothingAsset || LODIndex < 0 || LODIndex >= ClothingAsset->LodData.Num())
    {
        return;
    }

    IMutableClothingModule* ClothingModule = FModuleManager::LoadModulePtr<IMutableClothingModule>("MutableClothing");
    if (!ClothingModule)
    {
        return;
    }

    // 准备过渡数据（直接取自资产现有数据）
    TArray<TArrayView<FMeshToMeshVertData>> LODRenderData;
    for (int32 i = 0; i < ClothingAsset->LodData.Num(); ++i)
    {
        LODRenderData.Add(ClothingAsset->LodData[i].TransitionUpSkinData);
    }

    // 更新指定 LOD 的模拟数据
    bool bSuccess = ClothingModule->UpdateClothSimulationLOD(LODIndex, *ClothingAsset, LODRenderData);
    if (bSuccess)
    {
        ClothingModule->FixLODTransitionMappings(LODIndex, *ClothingAsset);
        UE_LOG(LogTemp, Log, TEXT("MutableClothing: LOD %d updated successfully."), LODIndex);
    }
}
```

> 注意：此示例假设服装资产已由 Mutable 生成并包含有效数据。实际使用时需结合 `UCustomizableObjectInstance` 获取对应资产。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mutable` | 提供自定义对象系统核心，本插件依赖其运行时模块 |

> 其他依赖如 `ClothingSystemRuntimeCommon`、`Engine` 等为标准服装模块，不在此列出。

---

## 维护状态

### 近期更新

- 2025-04-23 `939cc6e5` — 使用 FortniteClient 构建目标将文件转换为具有 dllstorage 的方法/静态变量格式
- 2025-02-24 `bfdb0b51` — [Mutable] 增强服装顶点遮罩生成对无效数据的鲁棒性
- 2025-02-19 `f1c141d0` — [Mutable] 将服装物理裁剪移入 Mutable 外部数据处理插件

### 维护评价

- **创建时间**：2025-02-19，距今不到半年，属于非常新的插件。
- **近期更新**：最近一次更新（2025-04-23）为构建配置调整；实质性功能更新在2025-02-24（鲁棒性修复）和2025-02-19（初始功能搬迁）。
- **活跃度**：维护活跃，尤其考虑到 Mutable 生态正在快速迭代。
- **已知问题**：文档较少，仅提供接口签名；作为实验性插件，API 可能在未来版本变化。
- **推荐使用**：若你正在使用 Mutable 5.7+ 版本并需要服装物理模拟，此插件是必须启用的。建议密切关注更新，及时适配 API 变更。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutableClothing)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mutable-overview/)（Mutable 通用文档，服装集成部分请参考版本配套说明）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mutable/Tests)（Mutable 相关测试，部分可能涉及本插件）