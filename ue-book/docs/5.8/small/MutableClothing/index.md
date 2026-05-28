# Mutable Clothing

> Adds Mutable functionality to work with clothing

| 属性 | 值 |
|---|---|
| 中文名 | 可变衣物 |
| 分类 | Mutable |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableClothing` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableClothing) | |

## 用途

MutableClothing 是 [Mutable](./Mutable.md) 自定义角色系统的辅助插件，专门处理布料模拟与 Mutable LOD 系统之间的集成问题。

当 Mutable 根据角色配置动态生成不同 LOD 级别的网格体时，衣物（Cloth）模拟系统需要知道每个 LOD 级别的顶点映射关系，才能正确地：
1. 将布料模拟结果应用到对应 LOD 的渲染网格上
2. 处理不同 LOD 之间的过渡映射（避免切换 LOD 时布料抖动或穿模）

此插件将衣物物理裁剪（clipping）逻辑从 Mutable 主体中解耦出来，作为外部数据操作插件存在。

## 使用场景

- 你的游戏使用 Mutable 做角色自定义系统（如换装、捏脸），且角色衣物使用了 Chaos Cloth 物理模拟
- 你需要在不同 LOD 级别下保持布料模拟的正确性
- 你需要处理 Mutable 动态生成网格时的布料数据迁移

## 蓝图用法

此插件为纯 C++ Runtime 模块，**不包含任何蓝图节点**。所有功能通过 `IMutableClothingModule` 接口在 C++ 层调用。

## C++ 用法

### 头文件引入

```cpp
#include "MutableClothingModule.h"
```

### 核心 API

插件通过模块接口 `IMutableClothingModule` 暴露两个核心函数：

| 函数 | 说明 |
|---|---|
| `UpdateClothSimulationLOD` | 根据指定的模拟 LOD 索引，更新衣物资产及其关联的渲染数据 |
| `FixLODTransitionMappings` | 修复指定 LOD 级别的布料过渡映射关系 |

### 基本用法

通过模块接口获取实例并调用：

```cpp
#include "MutableClothingModule.h"

// 获取 MutableClothing 模块实例
IMutableClothingModule& MutableClothingModule = FModuleManager::GetModuleChecked<IMutableClothingModule>("MutableClothing");

// 更新布料模拟 LOD
// InSimulationLODIndex: 目标模拟 LOD 索引
// InOutClothingAsset: 待更新的衣物资产（会被就地修改）
// InOutAttachedLODsRenderData: 各 LOD 级别的网格到网格顶点映射数据
MutableClothingModule.UpdateClothSimulationLOD(
    TargetLODIndex,
    ClothingAsset,
    AttachedLODsRenderData
);

// 修复 LOD 过渡映射
MutableClothingModule.FixLODTransitionMappings(
    TargetLODIndex,
    ClothingAsset
);
```

## Demo 示例

```cpp
// MutableClothingExample.h
#pragma once

#include "CoreMinimal.h"
#include "MutableClothingModule.h"

class FMutableClothingExample
{
public:
    /** 在 Mutable 网格更新后同步布料数据 */
    static bool SyncClothAfterMutableUpdate(
        int32 SimulationLODIndex,
        UClothingAssetCommon& ClothingAsset,
        TConstArrayView<TArrayView<FMeshToMeshVertData>> LODsRenderData);
};
```

```cpp
// MutableClothingExample.cpp
#include "MutableClothingExample.h"

bool FMutableClothingExample::SyncClothAfterMutableUpdate(
    int32 SimulationLODIndex,
    UClothingAssetCommon& ClothingAsset,
    TConstArrayView<TArrayView<FMeshToMeshVertData>> LODsRenderData)
{
    IMutableClothingModule* MutableClothingModule = 
        FModuleManager::GetModulePtr<IMutableClothingModule>("MutableClothing");
    
    if (!MutableClothingModule)
    {
        UE_LOG(LogTemp, Warning, TEXT("MutableClothing module not loaded"));
        return false;
    }

    // 更新布料模拟 LOD
    if (!MutableClothingModule->UpdateClothSimulationLOD(
            SimulationLODIndex, ClothingAsset, LODsRenderData))
    {
        return false;
    }

    // 修复 LOD 间过渡映射
    MutableClothingModule->FixLODTransitionMappings(
        SimulationLODIndex, ClothingAsset);

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mutable` | Mutable 自定义角色系统（.uplugin 显式依赖） |

无特殊依赖（仅标准 Core/Engine 等），衣物模拟相关类型（`UClothingAssetCommon`、`FMeshToMeshVertData`）属于 Engine 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 新格式 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | DLL 导出符号规范化（编译兼容性修复） |
| 2025-02-24 | `bfdb0b51` | [Mutable] Robustify clothing vertex remove mask generation against invalid data. | 增强衣物顶点移除掩码生成的健壮性 |
| 2025-02-19 | `f1c141d0` | [Mutable] Move clothing physics clipping in a mutable external data manipulation plugin. | 首次提交：将衣物物理裁剪逻辑独立为 Mutable 外部插件 |

### 维护评价

此插件处于**实验性阶段**，源码极小（仅 2 个文件），功能高度聚焦。自 2025-02 创建以来，仅有 1 次实质性功能修复（顶点掩码健壮性），其余为维护性改动。最近一次更新在 2026-04，说明仍有人在维护编译兼容性。

**注意事项**：
- 标记为 `IsExperimentalVersion=true`，API 可能变更
- `EnabledByDefault=false`，需要在插件设置中手动启用
- 高度依赖 Mutable 主插件，仅在使用 Mutable 角色自定义 + Chaos Cloth 布料模拟时才有用

**推荐**：如果你的项目使用 Mutable 做角色自定义且包含布料衣物，建议启用此插件。否则无需关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableClothing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Shared/FunctionalTests/GameTests/MutableClothingTests)（无）