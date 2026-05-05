# Landscape Patch

> Support for adding landscape patches- components that can be attached to meshes to affect the landscape as the mesh is repositioned.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI 样式资源） |
| 模块 | `LandscapePatch` (Runtime), `LandscapePatchEditorOnly` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/LandscapePatch) | |

## 用途

LandscapePatch 解决的核心问题是：**如何让网格体（Mesh）在场景中移动时，自动影响其周围的地形高度图和权重图**。

传统地形编辑是静态的——你在编辑器里画好地形就固定了。但很多游戏场景需要地形随物体动态变化，比如：陨石坑、脚印、可变形的地面。LandscapePatch 通过将"补丁"组件附加到网格体上，当网格体移动时，补丁会自动触发地形更新，将影响区域应用到地形的 Edit Layer 系统中。

该插件基于 UE5 的 Landscape Edit Layer 架构，每个补丁组件通过 GUID 绑定到一个 `ULandscapePatchEditLayer`，并通过 `Priority` 值决定多个补丁之间的执行顺序。

## 使用场景

- 你需要让一个网格体（如陨石、车辆）在地形上留下凹陷效果 → 将 Heightmap Patch 组件附加到该网格体
- 你需要根据物体位置动态修改地形权重图（如雪地脚印） → 使用 Weightmap Patch 组件
- 你有多个需要影响地形的物体，需要控制它们的叠加顺序 → 通过 Priority 系统排序
- 你正在从旧版 LandscapePatchManager 迁移 → 插件提供自动迁移路径

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RequestLandscapeUpdate` | 请求地形刷新，使补丁的修改生效 | `ULandscapePatchComponent` |
| `SetIsEnabled` | 启用/禁用补丁（不删除组件的情况下临时关闭效果） | `ULandscapePatchComponent` |
| `IsEnabled` | 查询补丁是否启用 | `ULandscapePatchComponent` |
| `SetPriority` | 设置补丁优先级（数值越大越晚应用，可覆盖前面的效果） | `ULandscapePatchComponent` |
| `GetPriority` | 获取当前优先级 | `ULandscapePatchComponent` |
| `SetEditLayerGuid` | 绑定补丁到指定的 Edit Layer | `ULandscapePatchComponent` |
| `GetEditLayerGuid` | 获取当前绑定的 Edit Layer GUID | `ULandscapePatchComponent` |
| `SetLandscape` | 指定目标地形 | `ULandscapePatchComponent` |
| `GetLandscape` | 获取当前目标地形 | `ULandscapePatchComponent` |
| `GetLandscapeHeightmapCoordsToWorld` | 获取高度图坐标到世界坐标的变换（用于将补丁映射到地形空间） | `ULandscapePatchComponent` |

### 使用示例（蓝图描述）

**基本用法：创建一个影响地形的补丁**

1. 创建一个 Blueprint Actor，添加一个 Static Mesh Component（如球体）
2. 为其添加一个 `ULandscapePatchComponent` 的子类（如 `ULandscapeTexturePatch`，如果存在具体实现）
3. 在 Details 面板中设置 `Landscape` 指向场景中的 ALandscape
4. 设置 `Edit Layer` 为一个 Patch 类型的 Edit Layer（或让插件自动创建）
5. 移动物体时，地形会自动更新

**控制多个补丁的叠加顺序**

1. 在 Details 面板中设置各补丁的 `Priority` 值
2. Priority 值小的先应用，值大的后应用（可覆盖前面的效果）
3. 新创建的补丁默认会自动获取当前最高 Priority + 1（取决于 `PriorityInitialization` 设置）

## C++ 用法

### 头文件引入

```cpp
#include "LandscapePatchComponent.h"
#include "LandscapePatchEditLayer.h"
```

### 基本用法

`ULandscapePatchComponent` 是抽象基类，不能直接实例化。你需要创建子类并实现关键虚函数。

```cpp
// 创建自定义 Patch 组件（继承 ULandscapePatchComponent）
UCLASS()
class UMyHeightPatch : public ULandscapePatchComponent
{
    GENERATED_BODY()
public:
    // 声明该补丁可以影响高度图
    virtual bool CanAffectHeightmap() const override { return true; }
    
    // 声明该补丁可以影响权重图
    virtual bool CanAffectWeightmap() const override { return true; }
    virtual bool CanAffectWeightmapLayer(const FName& InLayerName) const override
    {
        // 只影响特定图层
        return InLayerName == FName("Snow");
    }
};
```

> 来源: `LandscapePatchComponent.h` — `CanAffectHeightmap()`, `CanAffectWeightmap()`, `CanAffectWeightmapLayer()` 虚函数声明

### 进阶用法

**Priority 初始化策略**（创建补丁时如何确定初始优先级）：

```cpp
// 在子类构造函数中设置优先级初始化策略
UMyHeightPatch::UMyHeightPatch(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // AcquireHighest: 自动获取当前最高优先级（默认行为）
    // KeepOriginal: 保持原型值不变（适合用 Priority 做分类）
    // SmallIncrement: 在原型值上加 0.01（适合复制补丁时保持大致顺序）
    PriorityInitialization = ELandscapePatchPriorityInitialization::AcquireHighest;
}
```

> 来源: `LandscapePatchComponent.h` — `ELandscapePatchPriorityInitialization` 枚举

**绑定到 Edit Layer**：

```cpp
// 手动绑定到指定 Landscape 的 Patch Edit Layer
void BindToLandscapePatchLayer(ULandscapePatchComponent* Patch, ALandscape* Landscape)
{
    Patch->SetLandscape(Landscape);
    // 插件会自动查找或创建 ULandscapePatchEditLayer
    // 也可通过 SetEditLayerGuid 直接指定
}
```

> 来源: `LandscapePatchComponent.cpp` — `BindToLandscape()` 逻辑

**从旧版 PatchManager 迁移**：

```cpp
// 旧版 PatchManager 已废弃（5.7），系统会在加载时自动迁移
// 也可以手动触发：
// 控制台命令: LandscapePatch.FixPatchBindings
// 或在 CVar: LandscapePatch.AutoMigrateLegacyListToPrioritySystem (默认 true)
```

> 来源: `LandscapePatchManager.cpp` — `CVarMigrateLegacyPatchListToPrioritySystem` 和 `MigrateToPrioritySystemAndDeleteInternal()`

## Demo 示例

### 最小自定义 Patch 组件

```cpp
// MyHeightPatch.h
#pragma once

#include "LandscapePatchComponent.h"
#include "MyHeightPatch.generated.h"

UCLASS(Blueprintable, BlueprintType, meta = (DisplayName = "My Height Patch"))
class MYGAME_API UMyHeightPatch : public ULandscapePatchComponent
{
    GENERATED_BODY()

public:
    UMyHeightPatch(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

    // 声明影响能力
    virtual bool CanAffectHeightmap() const override { return bAffectsHeight; }
    virtual bool CanAffectWeightmap() const override { return bAffectsWeight; }
    virtual bool CanAffectWeightmapLayer(const FName& InLayerName) const override
    {
        return bAffectsWeight && InLayerName == WeightLayerName;
    }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Patch Settings")
    bool bAffectsHeight = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Patch Settings")
    bool bAffectsWeight = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Patch Settings", meta = (EditCondition = "bAffectsWeight"))
    FName WeightLayerName = FName("Layer0");

    // 补丁的实际渲染逻辑需要实现 ILandscapeEditLayerRenderer 的方法：
    // GetEditLayerRendererDebugName, GetRendererStateInfo, GetRenderItems, RenderLayer
    // 这些是 Editor-only 的接口方法
};
```

```cpp
// MyHeightPatch.cpp
#include "MyHeightPatch.h"

UMyHeightPatch::UMyHeightPatch(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "Landscape",
    "LandscapePatch",  // 引用 LandscapePatch 模块
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Landscape` | 地形系统核心模块，提供 Edit Layer、Landscape Actor 等 |
| `Engine` | 引擎核心（World、Actor、Component 等） |
| `RenderCore` | 渲染核心（纹理拷贝等 GPU 操作） |
| `RHI` | 渲染硬件接口（`FRHICommandListImmediate`） |
| `Renderer` | 渲染器模块 |
| `Projects` | 插件管理（`IPluginManager`） |
| `LevelEditor` | 编辑器级别操作（仅编辑器构建时，用于迁移操作） |
| `TypedElementRuntime` | 类型化元素运行时（仅编辑器构建时） |
| `UnrealEd` | 编辑器工具（`FScopedTransaction`，仅编辑器构建时） |

## 架构概览

```
ULandscapePatchComponent (抽象基类, Blueprintable)
├── 绑定到 ALandscape 的 Edit Layer (via FGuid)
├── 通过 Priority 排序
├── 实现 ILandscapeEditLayerRenderer 接口（子类负责实际渲染逻辑）
│
ULandscapePatchEditLayer (Edit Layer 类型)
├── 继承自 ULandscapePatchEditLayerProcedural
├── 维护 RegisteredPatches 列表（按 Priority 排序）
├── 在 GetEditLayerRendererStates 中将 patches 作为 renderers 暴露给合并系统
│
ADEPRECATED_LandscapePatchManager (已废弃)
├── 旧版 patch 管理器，5.7 中已废弃
├── 加载时自动迁移到 Priority 系统
└── 所有 API 标记为 DeprecatedFunction
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-10 | `72fe3c4` | 修复 Undo 操作导致的 assert 错误：Patch Edit Layer 在 Undo 时的标志位处理问题，以及在 Selection 模式下修改 patch transform 时正确标记 landscape 为 dirty |
| 2025-10-01 | `12cc341` | 添加 Landscape Patch 组件、插件和 Edit Layer 的图标，修复 Edit Layer 类缺少 class thumbnail 的问题 |
| 2025-09-24 | `1669ebf` | 修复注释中的拼写错误 |

### 维护评价

- **创建时间**：2022 年 4 月（最初在 Experimental 目录下），2025 年 9 月迁移到 Editor 目录
- **最近更新频率**：2025 年 9-10 月有 3 次提交，属于活跃维护期
- **重大变更**：5.6/5.7 中完成了从旧版 PatchManager 到 Priority 系统的重大架构重构。`ADEPRECATED_LandscapePatchManager` 被完全废弃，所有旧 API 均标记为 `DeprecatedFunction`
- **活跃维护**：是，该插件仍在积极开发中
- **已知限制**：目前仅支持编辑器环境（`IsEditorOnly() = true`），不支持运行时地形编辑
- **推荐使用**：✅ 推荐。这是 UE5 官方的地形动态修改方案，架构清晰，与 Edit Layer 系统深度集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/LandscapePatch)
- 官方文档（无，.uplugin 中 DocsURL 为空）
- 测试用例（未发现独立测试文件）
