# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

Variant Manager Content 是 [Datasmith](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/) Variant Manager 插件的**数据层**。它定义了 Variant Manager 系统中所有核心数据类（`ULevelVariantSets`、`UVariantSet`、`UVariant`、`UPropertyValue` 等）以及运行时 Actor（`ALevelVariantSetsActor`、`ASwitchActor`），负责存储、序列化和应用变体数据。

该插件解决的核心问题是：在建筑可视化、产品配置器等场景中，需要在同一关卡内快速切换大量对象的属性组合（材质、位置、可见性等），而 Variant Manager 内容插件提供了这些"属性快照"的底层存储和执行框架。

**注意**：此插件标记为 `IsBetaVersion=true`，仍处于 Beta 状态。

## 使用场景

- **产品配置器**：你在做汽车/家具等产品展示 → 用 Variant Manager 记录不同配置（颜色、配件），运行时通过 `SwitchOn()` 一键切换
- **建筑可视化**：同一空间需要展示多种设计方案 → 用 VariantSet 组织方案，Variant 存储每种方案的属性快照
- **灯光方案切换**：需要在同一场景中切换不同的灯光/氛围设置 → 捕获灯光属性到 Variant，运行时调用切换
- **SwitchActor 场景切换**：需要在多个子 Actor 之间快速切换可见性（如 A/B 方案模型）→ 使用 SwitchActor

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLevelVariantSets` | 获取 LevelVariantSets 资产（可选加载） | `ALevelVariantSetsActor` |
| `SetLevelVariantSets` | 设置关联的 LevelVariantSets 资产 | `ALevelVariantSetsActor` |
| `SwitchOnVariantByName` | 通过名称切换到指定变体 | `ALevelVariantSetsActor` |
| `SwitchOnVariantByIndex` | 通过索引切换到指定变体 | `ALevelVariantSetsActor` |
| `GetNumVariantSets` | 获取 VariantSet 数量 | `ULevelVariantSets` |
| `GetVariantSet` | 按索引获取 VariantSet | `ULevelVariantSets` |
| `GetVariantSetByName` | 按名称获取 VariantSet | `ULevelVariantSets` |
| `GetNumVariants` | 获取 Variant 数量 | `UVariantSet` |
| `GetVariant` | 按索引获取 Variant | `UVariantSet` |
| `GetVariantByName` | 按名称获取 Variant | `UVariantSet` |
| `SwitchOn` | 激活此 Variant（应用所有捕获的属性） | `UVariant` |
| `IsActive` | 检查 Variant 是否处于激活状态（属性未被修改） | `UVariant` |
| `GetNumActors` | 获取此 Variant 绑定的 Actor 数量 | `UVariant` |
| `GetActor` | 按索引获取绑定的 Actor | `UVariant` |
| `GetOptions` | 获取 SwitchActor 的子 Actor 列表 | `ASwitchActor` |
| `GetSelectedOption` | 获取当前选中的子 Actor 索引 | `ASwitchActor` |
| `SelectOption` | 按索引选中一个子 Actor（切换可见性） | `ASwitchActor` |
| `SetDisplayText` / `GetDisplayText` | 设置/获取显示名称 | `UVariant`, `UVariantSet` |
| `SetThumbnailFromTexture` | 从纹理设置缩略图 | `UVariant`, `UVariantSet` |
| `SetThumbnailFromFile` | 从文件路径设置缩略图 | `UVariant`, `UVariantSet` |
| `SetThumbnailFromCamera` | 从摄像机变换生成缩略图 | `UVariant`, `UVariantSet` |
| `SetThumbnailFromEditorViewport` | 从编辑器视口生成缩略图 | `UVariant`, `UVariantSet` |
| `GetThumbnail` | 获取缩略图纹理 | `UVariant`, `UVariantSet` |
| `HasRecordedData` | 检查属性是否有记录的数据 | `UPropertyValue` |
| `GetFullDisplayString` | 获取属性的完整路径显示字符串 | `UPropertyValue` |
| `GetPropertyTooltip` | 获取属性的工具提示文本 | `UPropertyValue` |

### 使用示例（蓝图描述）

**运行时切换 Variant**：

1. 在场景中放置 `ALevelVariantSetsActor`
2. 在 Details 面板中设置 `LevelVariantSets` 属性指向你的 `.LevelVariantSets` 资产
3. 在蓝图中：获取 Actor 引用 → 调用 `SwitchOnVariantByName("VariantSetName", "VariantName")`
4. 所有关联的 Actor 属性会被自动恢复到录制时的状态

**SwitchActor 可见性切换**：

1. 在场景中放置 `ASwitchActor`
2. 将多个子 Actor 附加到它下面（作为不同"选项"）
3. 在蓝图中：获取 SwitchActor 引用 → 调用 `SelectOption(0)` 显示第一个子 Actor，`SelectOption(1)` 显示第二个
4. 或者在 Variant Manager 中捕获 SwitchActor 的 "Selected Option" 属性

**Variant 依赖链**：

Variant 支持依赖关系（`FVariantDependency`），当一个 Variant 被激活时，它的依赖 Variant 也会自动激活。蓝图中可通过 `GetNumDependencies` / `GetDependency` 管理依赖。

## C++ 用法

### 头文件引入

```cpp
#include "LevelVariantSets.h"
#include "LevelVariantSetsActor.h"
#include "VariantSet.h"
#include "Variant.h"
#include "VariantObjectBinding.h"
#include "PropertyValue.h"
#include "SwitchActor.h"
```

### 基本用法

**遍历 LevelVariantSets 中的所有变体**：

```cpp
// 来源: LevelVariantSets.h / VariantSet.h
ULevelVariantSets* LVS = LevelVariantSetsActor->GetLevelVariantSets(true);
if (LVS)
{
    for (int32 i = 0; i < LVS->GetNumVariantSets(); ++i)
    {
        UVariantSet* VariantSet = LVS->GetVariantSet(i);
        UE_LOG(LogTemp, Log, TEXT("VariantSet: %s"), *VariantSet->GetDisplayText().ToString());
        
        for (int32 j = 0; j < VariantSet->GetNumVariants(); ++j)
        {
            UVariant* Variant = VariantSet->GetVariant(j);
            UE_LOG(LogTemp, Log, TEXT("  Variant: %s, Actors: %d"), 
                *Variant->GetDisplayText().ToString(), Variant->GetNumActors());
        }
    }
}
```

**按名称激活 Variant**：

```cpp
// 来源: LevelVariantSetsActor.h
ALevelVariantSetsActor* LVSActor = /* ... */;
bool bSuccess = LVSActor->SwitchOnVariantByName(TEXT("Interior"), TEXT("Modern Style"));
```

**编程式操作 SwitchActor**：

```cpp
// 来源: SwitchActor.h / SwitchActor.cpp
ASwitchActor* SwitchActor = /* ... */;
TArray<AActor*> Options = SwitchActor->GetOptions(); // 按 FName 排序
SwitchActor->SelectOption(1); // 切换到第二个子 Actor
int32 CurrentSelection = SwitchActor->GetSelectedOption();
```

### 进阶用法

**属性捕获与应用系统**：

`UPropertyValue` 是 Variant Manager 的属性捕获核心。每个 `UVariant` 通过 `UVariantObjectBinding` 绑定到特定 Actor，每个 binding 包含一组 `UPropertyValue` 来记录该 Actor 的属性快照。

```cpp
// 来源: VariantObjectBinding.h, PropertyValue.h
UVariant* Variant = /* ... */;
for (UVariantObjectBinding* Binding : Variant->GetBindings())
{
    UObject* BoundObject = Binding->GetObject();
    for (UPropertyValue* PropValue : Binding->GetCapturedProperties())
    {
        if (PropValue->HasRecordedData())
        {
            // 检查当前值是否与录制值一致
            bool bIsCurrent = PropValue->IsRecordedDataCurrent();
            UE_LOG(LogTemp, Log, TEXT("Property: %s, Current: %s"),
                *PropValue->GetFullDisplayString(),
                bIsCurrent ? TEXT("Yes") : TEXT("No"));
        }
    }
    // 执行绑定的函数调用器
    Binding->ExecuteAllTargetFunctions();
}
```

**PropertyValue 类型层次**：

| 类 | 用途 |
|---|---|
| `UPropertyValue` | 基类，处理通用属性（float、int、bool、vector 等） |
| `UPropertyValueColor` | FColor/FLinearColor 属性，使用 property setter 保持线性颜色接口 |
| `UPropertyValueMaterial` | 材质覆盖属性，处理 OverrideMaterials 特殊情况 |
| `UPropertyValueOption` | SwitchActor 的选择索引属性 |
| `UPropertyValueSoftObject` | 软引用（TSoftObjectPtr）属性 |
| `UPropertyValueTransform` | 已废弃，仅为 4.21 向后兼容保留 |
| `UPropertyValueVisibility` | 已废弃，仅为向后兼容保留 |

**EPropertyValueCategory 枚举**：

```cpp
// 来源: PropertyValue.h
enum class EPropertyValueCategory : uint8
{
    Undefined        = 0,
    Generic          = 1,
    RelativeLocation = 2,
    RelativeRotation = 4,
    RelativeScale3D  = 8,
    Visibility       = 16,
    Material         = 32,
    Color            = 64,
    Option           = 128
};
```

## Demo 示例

### 最小 Variant 切换示例

```cpp
// MyVariantSwitcher.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyVariantSwitcher.generated.h"

class ALevelVariantSetsActor;

UCLASS()
class AMyVariantSwitcher : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category="Config")
    TSoftObjectPtr<ALevelVariantSetsActor> LVSTarget;

    UFUNCTION(BlueprintCallable)
    void SwitchToVariant(FString VariantSetName, FString VariantName)
    {
        ALevelVariantSetsActor* LVSActor = LVSTarget.Get();
        if (LVSActor)
        {
            LVSActor->SwitchOnVariantByName(VariantSetName, VariantName);
        }
    }
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "VariantManagerContent",
    "Core",
    "CoreUObject",
    "Engine"
});
```

## 模块依赖

### VariantManagerContent (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `RenderCore` | 渲染核心（缩略图生成） |
| `RHI` | 渲染硬件接口（缩略图生成） |
| `EditorFramework` | 编辑器框架（仅编辑器构建） |
| `UnrealEd` | 编辑器功能（仅编辑器构建） |
| `BlueprintGraph` | 蓝图图表（仅编辑器构建，FunctionCaller 管理） |

### VariantManagerContentEditor (Editor)

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 资产类型定义 |
| `ContentBrowser` | 内容浏览器集成 |
| `Core` / `CoreUObject` / `Engine` | 基础依赖 |
| `EditorFramework` / `UnrealEd` | 编辑器框架 |
| `ToolMenus` | 工具菜单集成 |
| `InputCore` | 键盘输入（ListView 控制） |
| `Slate` / `SlateCore` | UI 框架 |
| `VariantManagerContent` | Runtime 模块依赖 |
| `WorkspaceMenuStructure` | 工作区菜单结构 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-10 | `9803c443cfab` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏到源文件 — 构建优化，减少编译时间 |
| 2025-05-30 | `52e3dac151e1` | 使用 UnrealCodeFixup 更新头文件，将 DLL 导出标记从类型移到方法/静态变量上 — DLL 导出规范化 |
| 2025-04-23 | `6ae573356bbf` | 同上，批量转换所有文件的 DLL 导出方式 — 全面的 API 导出重构 |

### 维护评价

- **创建时间**：2018 年 9 月，随 Datasmith Variant Manager 一起引入
- **最近更新**：2025 年 7 月，但近三次更新均为构建系统/代码规范化修改，**无功能性更新**
- **维护状态**：⚠️ 维护不活跃 — 长期无实质性功能更新，近期修改均为 Epic 的全局代码修复工具自动应用
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，自 2018 年创建以来一直处于 Beta
- **已知限制**：
  - Beta 状态，API 可能在未来版本发生变化
  - `UPropertyValueTransform` 和 `UPropertyValueVisibility` 已废弃，仅为向后兼容保留
  - `LevelVariantSets` 中的 World Context 管理依赖编辑器事件，在打包构建中有不同行为
- **推荐**：适合在 Datasmith 工作流中使用；如果只是运行时切换 Actor 可见性，`SwitchActor` 单独使用也很实用。不建议在不使用 Variant Manager UI 的情况下直接操作底层数据类。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档（Datasmith）](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
