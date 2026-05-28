# Variant Manager

> Manages scene actor variants

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager) | |

## 用途

Variant Manager 是一个用于管理场景 Actor 属性变体的编辑器插件，主要服务于**产品配置器**和**建筑可视化（ArchViz）**场景。

核心思路是：将场景中 Actor 的各种属性（位置、旋转、材质、可见性、自定义属性等）捕获为"属性快照"，然后将这些快照组织成层级结构：`LevelVariantSets → VariantSet → Variant → Actor Binding → Property Capture`。用户可以通过切换 Variant 来快速切换场景中一组 Actor 的属性状态。

典型使用场景：一个产品展厅有多种颜色配置方案，每种方案对应一组灯光颜色、材质参数和物体位置的组合。Variant Manager 让你把这些配置方案管理起来，并在运行时通过蓝图或 Python 脚本切换。

**注意**：此插件默认禁用且标记为 Beta 版本，需要在项目设置中手动启用。它与 Datasmith 工作流紧密关联。

## 使用场景

- 你在做**建筑可视化**项目，需要管理同一场景的多种设计方案（家具布局、材质配色、灯光氛围）→ 用 Variant Manager 管理设计方案变体
- 你在做**产品配置器**，用户可以在运行时切换产品颜色、材质、配件等 → 用 Variant Manager 捕获属性变体并运行时切换
- 你需要用 **Python 脚本**批量创建和管理大量变体配置 → 用 VariantManagerBlueprintLibrary 提供的静态函数
- 你需要记录和回放 Actor 属性的变化 → 用 Record/Apply 功能

## 蓝图用法

所有蓝图可用节点集中在 `UVariantManagerBlueprintLibrary` 中（通过 Python 脚本或蓝图调用）。

### 核心节点

#### 资产与场景管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLevelVariantSetsAsset` | 在指定内容路径创建新的 LevelVariantSets 资产 | `UVariantManagerBlueprintLibrary` |
| `CreateLevelVariantSetsActor` | 在当前场景中创建 LevelVariantSetsActor 并关联资产 | `UVariantManagerBlueprintLibrary` |
| `GetCapturableProperties` | 获取指定 Actor 或类可捕获的属性路径列表 | `UVariantManagerBlueprintLibrary` |

#### VariantSet 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddVariantSet` | 将 VariantSet 添加到 LevelVariantSets | `UVariantManagerBlueprintLibrary` |
| `RemoveVariantSet` | 从 LevelVariantSets 中移除 VariantSet | `UVariantManagerBlueprintLibrary` |
| `RemoveVariantSetByName` | 按名称移除 VariantSet | `UVariantManagerBlueprintLibrary` |

#### Variant 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddVariant` | 将 Variant 添加到 VariantSet | `UVariantManagerBlueprintLibrary` |
| `RemoveVariant` | 从 VariantSet 中移除 Variant | `UVariantManagerBlueprintLibrary` |
| `RemoveVariantByName` | 按名称移除 Variant | `UVariantManagerBlueprintLibrary` |

#### Actor 绑定与属性捕获

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActorBinding` | 将 Actor 绑定到 Variant | `UVariantManagerBlueprintLibrary` |
| `CaptureProperty` | 捕获指定 Actor 的指定属性到 Variant 中 | `UVariantManagerBlueprintLibrary` |
| `GetCapturedProperties` | 获取 Variant 中某个 Actor 已捕获的属性列表 | `UVariantManagerBlueprintLibrary` |
| `RemoveActorBinding` | 移除 Variant 中的 Actor 绑定 | `UVariantManagerBlueprintLibrary` |
| `RemoveActorBindingByName` | 按 Actor 名称移除绑定 | `UVariantManagerBlueprintLibrary` |
| `RemoveCapturedProperty` | 移除已捕获的属性 | `UVariantManagerBlueprintLibrary` |
| `RemoveCapturedPropertyByName` | 按属性路径移除已捕获的属性 | `UVariantManagerBlueprintLibrary` |

#### 属性录制与应用

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Record` | 将当前 Actor 的属性值录制到 PropertyVal | `UVariantManagerBlueprintLibrary` |
| `Apply` | 将 PropertyVal 中录制的值应用到 Actor | `UVariantManagerBlueprintLibrary` |
| `GetPropertyTypeString` | 获取属性的 C++ 类型字符串 | `UVariantManagerBlueprintLibrary` |

#### 依赖管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDependency` | 为 Variant 添加依赖关系 | `UVariantManagerBlueprintLibrary` |
| `SetDependency` | 设置指定索引的依赖关系 | `UVariantManagerBlueprintLibrary` |
| `DeleteDependency` | 删除指定索引的依赖关系 | `UVariantManagerBlueprintLibrary` |
| `GetDependencies` | 获取 Variant 的所有依赖关系 | `UVariantManagerBlueprintLibrary` |

#### 属性值访问器（PropertyAccessors）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetValueBool` / `GetValueBool` | 读写布尔属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueInt` / `GetValueInt` | 读写整型属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueFloat` / `GetValueFloat` | 读写浮点属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueString` / `GetValueString` | 读写字符串属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueVector` / `GetValueVector` | 读写向量属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueRotator` / `GetValueRotator` | 读写旋转属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueColor` / `GetValueColor` | 读写 FColor 属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueLinearColor` / `GetValueLinearColor` | 读写 FLinearColor 属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueQuat` / `GetValueQuat` | 读写四元数属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueObject` / `GetValueObject` | 读写 UObject 属性 | `UVariantManagerBlueprintLibrary` |

#### 函数调用器（FunctionCallers）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateDirectorBlueprint` | 获取或创建 Variant 关联的 Director 蓝图 | `UVariantManagerBlueprintLibrary` |
| `GetFunctionCallerNames` | 获取 Variant 中某个 Actor 的函数调用器名称列表 | `UVariantManagerBlueprintLibrary` |
| `GetFunctionCallerArguments` | 获取函数调用器的参数映射 | `UVariantManagerBlueprintLibrary` |
| `CreateFunctionCaller` | 创建函数调用器（指定签名类型） | `UVariantManagerBlueprintLibrary` |
| `AddFunctionCaller` | 添加函数调用器 | `UVariantManagerBlueprintLibrary` |
| `UpdateFunctionCallerArguments` | 更新函数调用器参数 | `UVariantManagerBlueprintLibrary` |
| `RemoveFunctionCaller` | 移除函数调用器 | `UVariantManagerBlueprintLibrary` |

### 使用示例（蓝图描述）

**场景：为场景中的 Actor 创建颜色变体**

1. 调用 `CreateLevelVariantSetsAsset` 创建 LevelVariantSets 资产（如 `"/Game/MyLevelVariantSets"`）
2. 调用 `CreateLevelVariantSetsActor` 在场景中放置对应的 Actor
3. 调用 `CreateVariantSet`（内部方法）创建 VariantSet（如 "红色方案"）
4. 调用 `AddVariant` 将 VariantSet 添加到 LevelVariantSets
5. 调用 `AddActorBinding` 将目标 Actor 绑定到 Variant
6. 调用 `CaptureProperty` 捕获目标属性（如 `"/Game/MyActor.StaticMeshComponent:Material"`）
7. 通过 `SetValueLinearColor` 设置捕获属性的值
8. 运行时调用 `Apply` 应用变体

## C++ 用法

### 头文件引入

```cpp
#include "VariantManagerModule.h"
#include "VariantManager.h"
#include "VariantManagerBlueprintLibrary.h"
```

### 基本用法

通过模块接口创建 Variant Manager 实例：

```cpp
// Source: Source/VariantManager/Public/VariantManagerModule.h
#include "VariantManagerModule.h"
#include "VariantManager.h"

// 检查模块是否可用
if (IVariantManagerModule::IsAvailable())
{
    // 获取模块实例
    IVariantManagerModule& Module = IVariantManagerModule::Get();
    
    // 为指定的 LevelVariantSets 创建 VariantManager 实例
    TSharedRef<FVariantManager> VariantManager = Module.CreateVariantManager(LevelVariantSets);
    
    // 初始化后即可使用
    VariantManager->InitVariantManager(LevelVariantSets);
}
```

### 从蓝图库创建完整工作流

```cpp
// Source: Source/VariantManager/Public/VariantManagerBlueprintLibrary.h
#include "VariantManagerBlueprintLibrary.h"

// 1. 创建资产
ULevelVariantSets* LevelVariantSets = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsAsset(
    TEXT("MyConfig"), TEXT("/Game"));

// 2. 创建场景 Actor
ALevelVariantSetsActor* Actor = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsActor(LevelVariantSets);

// 3. 创建 VariantSet 和 Variant（需通过 FVariantManager 内部 API）
// UVariant* Variant = VariantManager->CreateVariant(VariantSet);

// 4. 获取可捕获的属性
TArray<FString> Properties = UVariantManagerBlueprintLibrary::GetCapturableProperties(SomeActor);
```

### 进阶用法

使用 FVariantManager 直接操作捕获属性和变体绑定：

```cpp
// Source: Source/VariantManager/Public/VariantManager.h

// 获取 VariantManager 实例
FVariantManager& VManager = UVariantManagerBlueprintLibrary::GetVariantManager();
VManager.InitVariantManager(LevelVariantSets);

// 获取可捕获的属性列表
TArray<TSharedPtr<FCapturableProperty>> CapturableProps;
VManager.GetCapturableProperties({TargetActor}, CapturableProps);

// 创建属性捕获（直接捕获 Transform）
TArray<UPropertyValue*> TransformProps = VManager.CreateTransformPropertyCaptures(Bindings);

// 捕获可见性
TArray<UPropertyValue*> VisibilityProps = VManager.CreateVisibilityPropertyCaptures(Bindings);

// 捕获材质
TArray<UPropertyValue*> MaterialProps = VManager.CreateMaterialPropertyCaptures(Bindings);

// 创建对象绑定并自动捕获所有属性
TArray<UVariantObjectBinding*> Bindings = VManager.CreateObjectBindingsAndCaptures(
    {Actor1, Actor2}, {Variant1});

// 录制和应用属性
VManager.RecordProperty(SomePropertyValue);
VManager.ApplyProperty(SomePropertyValue);

// 调用 Director 函数
VManager.CallDirectorFunction(FName("OnVariantSwitched"), TargetBinding);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithContent` | Datasmith 资产内容支持（LevelVariantSets 等） |
| `LevelSequence` | 关键帧和属性动画序列支持 |

> 注：核心功能还依赖标准的 UnrealEd（编辑器 UI）、Slate（自定义面板）、PropertyEditor 等模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 到 UE_LOGF 宏 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | AutoViz 功能的 Variant Manager 小幅更新 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 将析构函数改为 = default |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 将析构函数改为 = default |

### 维护评价

- **创建时间**：2019 年 10 月，已有约 6 年历史
- **维护状态**：持续维护中，近期有功能性更新（AutoViz 相关改动）
- **Beta 状态**：插件至今仍标记为 `IsBetaVersion = true`，且默认禁用
- **活跃度**：过去一年内有多次提交，但大多为代码风格和编译警告修复，实质性功能更新较少
- **关联性**：与 Datasmith 和 AutoViz 工作流紧密关联，是 Epic Enterprise 产品线的一部分
- **推荐**：如果你使用 Datasmith 导入建筑/工业模型并需要管理设计方案变体，推荐使用。但需注意它仍是 Beta 状态，API 可能变动。对于非 Datasmith 工作流，此插件仍可独立使用，但需要手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)