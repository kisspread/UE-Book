# Variant Manager

> Manages scene actor variants

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（SVG 图标） |
| 模块 | `VariantManager` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/VariantManager) | |

## 用途

Variant Manager 是 UE5 的**场景变体管理器**，属于 Datasmith 工作流的一部分。它允许你为关卡中的 Actor 定义多组属性"快照"（Variant），然后在运行时或编辑器中一键切换这些变体。

核心概念：
- **LevelVariantSets**：顶层资产，包含多个 VariantSet
- **VariantSet**：一组相关变体的集合（如"颜色方案"）
- **Variant**：一个具体的变体（如"红色方案"），包含多个 Actor 绑定
- **ObjectBinding**：将一个 Actor 绑定到 Variant，记录该 Actor 的属性捕获
- **PropertyValue**：被捕获的具体属性值（如 Location、Material 等）

典型场景：建筑可视化中，一个 VariantSet 管理"地板材质"，Variant A 是大理石，Variant B 是木地板，切换 Variant 即可同时改变多个 Actor 的材质属性。

## 使用场景

- **建筑可视化（ArchViz）**：为同一场景定义不同装修方案（材质、灯光、家具布局）
- **产品配置器**：汽车颜色/轮毂/内饰的组合展示
- **Datasmith 工作流**：从 CAD/BIM 软件导入的模型，需要在 UE 中快速切换配置
- **场景预设管理**：保存和恢复场景中多个 Actor 的属性状态
- **运行时交互**：让用户在运行时通过 UI 切换场景配置

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Level Variant Sets Asset` | 在 Content Browser 创建新的 LevelVariantSets 资产 | `UVariantManagerBlueprintLibrary` |
| `Create Level Variant Sets Actor` | 在场景中放置 LevelVariantSetsActor 并关联资产 | `UVariantManagerBlueprintLibrary` |
| `Add Variant Set` | 向 LevelVariantSets 添加 VariantSet | `UVariantManagerBlueprintLibrary` |
| `Add Variant` | 向 VariantSet 添加 Variant | `UVariantManagerBlueprintLibrary` |
| `Add Actor Binding` | 将 Actor 绑定到 Variant | `UVariantManagerBlueprintLibrary` |
| `Capture Property` | 捕获 Actor 的指定属性到 Variant | `UVariantManagerBlueprintLibrary` |
| `Get Capturable Properties` | 获取 Actor/Class 所有可捕获的属性路径列表 | `UVariantManagerBlueprintLibrary` |
| `Get Captured Properties` | 获取 Variant 中某 Actor 已捕获的属性列表 | `UVariantManagerBlueprintLibrary` |
| `Record` | 从 Actor 重新录制属性值 | `UVariantManagerBlueprintLibrary` |
| `Apply` | 将录制的属性值应用到 Actor | `UVariantManagerBlueprintLibrary` |
| `Get Property Type String` | 获取属性的类型字符串（float/int/bool/vector 等） | `UVariantManagerBlueprintLibrary` |

### 属性访问器节点

| 节点 | 说明 | 类型 |
|---|---|---|
| `Set/Get Value Bool` | 读写布尔属性 | `bool` |
| `Set/Get Value Int` | 读写整数属性 | `int32` |
| `Set/Get Value Float` | 读写浮点属性 | `float` |
| `Set/Get Value String` | 读写字符串属性 | `FString` |
| `Set/Get Value Object` | 读写对象引用属性 | `UObject*` |
| `Set/Get Value Rotator` | 读写旋转属性 | `FRotator` |
| `Set/Get Value Color` | 读写颜色属性 | `FColor` |
| `Set/Get Value Linear Color` | 读写线性颜色属性 | `FLinearColor` |
| `Set/Get Value Vector` | 读写向量属性 | `FVector` |
| `Set/Get Value Quat` | 读写四元数属性 | `FQuat` |
| `Set/Get Value Vector4` | 读写四维向量属性 | `FVector4` |
| `Set/Get Value Vector2D` | 读写二维向量属性 | `FVector2D` |
| `Set/Get Value IntPoint` | 读写整数点属性 | `FIntPoint` |

### 依赖管理节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Dependency` | 向 Variant 添加依赖 | `UVariantManagerBlueprintLibrary` |
| `Set Dependency` | 设置指定索引的依赖 | `UVariantManagerBlueprintLibrary` |
| `Delete Dependency` | 删除指定索引的依赖 | `UVariantManagerBlueprintLibrary` |

### 删除节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remove Variant Set` | 从 LevelVariantSets 移除 VariantSet | `UVariantManagerBlueprintLibrary` |
| `Remove Variant` | 从 VariantSet 移除 Variant | `UVariantManagerBlueprintLibrary` |
| `Remove Actor Binding` | 从 Variant 移除 Actor 绑定 | `UVariantManagerBlueprintLibrary` |
| `Remove Captured Property` | 移除已捕获的属性 | `UVariantManagerBlueprintLibrary` |
| `Remove Variant Set By Name` | 按名称移除 VariantSet | `UVariantManagerBlueprintLibrary` |
| `Remove Variant By Name` | 按名称移除 Variant | `UVariantManagerBlueprintLibrary` |
| `Remove Actor Binding By Name` | 按名称移除 Actor 绑定 | `UVariantManagerBlueprintLibrary` |
| `Remove Captured Property By Name` | 按属性路径移除捕获 | `UVariantManagerBlueprintLibrary` |

### 使用示例（蓝图描述）

**创建完整的 Variant 配置：**

1. 调用 `Create Level Variant Sets Asset`（AssetName="MyVariants", AssetPath="/Game"）
2. 调用 `Create Level Variant Sets Actor` 传入上一步的资产
3. 调用 `Add Variant Set` 添加一个 VariantSet
4. 调用 `Add Variant` 向 VariantSet 添加 Variant
5. 调用 `Add Actor Binding` 将目标 Actor 绑定到 Variant
6. 调用 `Capture Property` 捕获具体属性（PropertyPath 如 "StaticMeshComponent.RelativeLocation"）
7. 修改 Actor 属性后调用 `Record` 录制新值
8. 之后随时调用 `Apply` 恢复到录制的值

**运行时切换 Variant：**

使用 `ALevelVariantSetsActor` 的 `Switch On Variant By Index` 或 `Switch On Variant By Name` 蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "VariantManagerModule.h"
#include "VariantManager.h"
#include "VariantManagerBlueprintLibrary.h"
#include "CapturableProperty.h"
```

### 基本用法

通过 `UVariantManagerBlueprintLibrary` 的静态函数进行脚本化操作（也是 Python API 的底层实现）：

```cpp
// 创建 LevelVariantSets 资产
ULevelVariantSets* LVS = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsAsset(
    TEXT("MyVariants"), TEXT("/Game"));

// 在场景中放置 Actor
ALevelVariantSetsActor* LVSActor = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsActor(LVS);

// 创建 VariantSet 和 Variant
UVariantSet* VarSet = NewObject<UVariantSet>(LVS);
UVariantManagerBlueprintLibrary::AddVariantSet(LVS, VarSet);

UVariant* Var = NewObject<UVariant>(VarSet);
UVariantManagerBlueprintLibrary::AddVariant(VarSet, Var);

// 绑定 Actor 并捕获属性
UVariantManagerBlueprintLibrary::AddActorBinding(Var, MyActor);
UPropertyValue* PropVal = UVariantManagerBlueprintLibrary::CaptureProperty(
    Var, MyActor, TEXT("StaticMeshComponent.RelativeLocation"));

// 录制和应用
UVariantManagerBlueprintLibrary::Record(PropVal);
UVariantManagerBlueprintLibrary::Apply(PropVal);
```

*来源：`VariantManagerBlueprintLibrary.cpp`*

### 进阶用法

通过 `IVariantManagerModule` 直接创建 `FVariantManager` 实例进行更底层的操作：

```cpp
// 获取模块接口
IVariantManagerModule& VMModule = IVariantManagerModule::Get();

// 创建 VariantManager 实例
TSharedRef<FVariantManager> VarManager = VMModule.CreateVariantManager(MyLevelVariantSets);

// 获取可捕获的属性
TArray<TSharedPtr<FCapturableProperty>> CapturableProps;
VarManager->GetCapturableProperties({MyActor}, CapturableProps);

// 创建属性捕获
TArray<UPropertyValue*> CapturedProps = VarManager->CreatePropertyCaptures(CapturableProps, Bindings);

// 快捷捕获 Transform/Visibility/Material
TArray<UPropertyValue*> TransformProps = VarManager->CreateTransformPropertyCaptures(Bindings);
TArray<UPropertyValue*> VisibilityProps = VarManager->CreateVisibilityPropertyCaptures(Bindings);
TArray<UPropertyValue*> MaterialProps = VarManager->CreateMaterialPropertyCaptures(Bindings);
```

*来源：`VariantManager.h`*

### 属性类型判断

`GetPropertyTypeString` 返回的类型字符串映射：

| C++ 类型 | 返回字符串 |
|---|---|
| `FStructProperty` (FVector) | `"vector"` |
| `FStructProperty` (FRotator) | `"rotator"` |
| `FStructProperty` (FColor) | `"color"` |
| `FStructProperty` (FLinearColor) | `"linear_color"` |
| `FStructProperty` (FQuat) | `"quat"` |
| `FStructProperty` (FVector4) | `"vector4"` |
| `FStructProperty` (FVector2D) | `"vector2d"` |
| `FStructProperty` (FIntPoint) | `"int_point"` |
| 浮点数 | `"float"` |
| 整数 | `"int"` |
| `FBoolProperty` | `"bool"` |
| `FStrProperty`/`FTextProperty`/`FNameProperty` | `"string"` |
| `FObjectProperty`/`FInterfaceProperty` | `"object"` |

## Demo 示例

### 最小完整示例（C++）

```cpp
// MyVariantManagerDemo.h
#pragma once
#include "CoreMinimal.h"

class FMyVariantManagerDemo
{
public:
    static void RunDemo(UWorld* World);
};
```

```cpp
// MyVariantManagerDemo.cpp
#include "MyVariantManagerDemo.h"
#include "VariantManagerBlueprintLibrary.h"
#include "LevelVariantSets.h"
#include "LevelVariantSetsActor.h"
#include "Variant.h"
#include "VariantSet.h"
#include "PropertyValue.h"

void FMyVariantManagerDemo::RunDemo(UWorld* World)
{
    // 1. 创建资产
    ULevelVariantSets* LVS = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsAsset(
        TEXT("DemoVariants"), TEXT("/Game"));
    if (!LVS) return;

    // 2. 放置 Actor
    ALevelVariantSetsActor* LVSActor = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsActor(LVS);

    // 3. 创建 VariantSet "Colors"
    UVariantSet* ColorSet = NewObject<UVariantSet>(LVS);
    UVariantManagerBlueprintLibrary::AddVariantSet(LVS, ColorSet);

    // 4. 创建 Variant "Red"
    UVariant* RedVariant = NewObject<UVariant>(ColorSet);
    UVariantManagerBlueprintLibrary::AddVariant(ColorSet, RedVariant);

    // 5. 假设场景中有一个 StaticMeshActor
    AStaticMeshActor* MeshActor = /* 从场景获取 */;
    UVariantManagerBlueprintLibrary::AddActorBinding(RedVariant, MeshActor);

    // 6. 捕获可见性属性
    UPropertyValue* VisProp = UVariantManagerBlueprintLibrary::CaptureProperty(
        RedVariant, MeshActor, TEXT("StaticMeshComponent.bVisible"));

    // 7. 设置值并录制
    if (VisProp)
    {
        UVariantManagerBlueprintLibrary::SetValueBool(VisProp, true);
    }

    // 8. 之后应用
    UVariantManagerBlueprintLibrary::Apply(VisProp);
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "VariantManager",
    "VariantManagerContent",
    "Core",
    "CoreUObject",
    "Engine",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器工具 |
| `PropertyPath` | 属性路径解析，用于捕获属性 |
| `VariantManagerContent` | 数据类（ULevelVariantSets、UVariant 等） |
| `AppFramework` | 颜色选择器 |
| `BlueprintGraph` | 蓝图函数 Director |
| `PropertyEditor` | 属性控件创建 |
| `SceneOutliner` | 场景大纲集成 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 工具菜单注册 |
| `VariantManagerContentEditor` | 内容编辑器模块 |

## 架构概览

### 核心类

| 类 | 职责 |
|---|---|
| `FVariantManager` | 核心管理器，处理所有 VariantSet/Variant/Binding 的增删改查、属性录制/应用 |
| `FVariantManagerModule` | 模块入口，注册 Tab Spawner 和编辑器委托 |
| `FLevelVariantSetsEditorToolkit` | 资产编辑器 Toolkit，管理编辑器标签页 |
| `SVariantManager` | 主 UI 面板，包含 Variant 树、Actor 列表、属性列表 |
| `FVariantManagerNodeTree` | 节点树数据结构，驱动 UI 展示 |
| `FVariantManagerSelection` | 选择状态管理 |
| `FVariantManagerPropertyCapturer` | 属性捕获工具，分析 Actor 的可捕获属性 |
| `UVariantManagerBlueprintLibrary` | 蓝图/Python API 入口 |
| `FCapturableProperty` | 可捕获属性的描述结构 |

### DisplayNode 层级

| 节点类型 | 说明 |
|---|---|
| `FVariantManagerVariantSetNode` | VariantSet 显示节点 |
| `FVariantManagerVariantNode` | Variant 显示节点 |
| `FVariantManagerActorNode` | Actor 绑定显示节点 |
| `FVariantManagerPropertyNode` | 属性显示节点基类 |
| `FVariantManagerColorPropertyNode` | 颜色属性节点 |
| `FVariantManagerEnumPropertyNode` | 枚举属性节点 |
| `FVariantManagerStringPropertyNode` | 字符串属性节点 |
| `FVariantManagerStructPropertyNode` | 结构体属性节点 |
| `FVariantManagerOptionPropertyNode` | 选项属性节点 |
| `FVariantManagerFunctionPropertyNode` | 函数属性节点 |

### 编辑器功能

- **拖拽支持**：Variant 树和 Actor 列表支持拖拽排序
- **剪贴板**：支持 Cut/Copy/Paste/Duplicate 操作
- **缩略图**：支持为 Variant 设置缩略图
- **搜索过滤**：Variant 树支持搜索过滤
- **自动捕获**：支持自动捕获属性变更
- **依赖管理**：Variant 之间可设置依赖关系
- **Undo/Redo**：完整支持编辑器撤销/重做

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 代码现代化，添加内联 gen.cpp 宏 |
| 2025-03-13 | `b059f7b46335` | Fix trivial unreachable code warnings | 编译警告修复 |
| 2024-11-09 | `66e9bb39ff7e` | Removed deprecated include order scopes | 代码清理，移除 5.2 弃用宏 |

### 维护评价

- **创建时间**：2019-10-04，约 7 年历史
- **实验性状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，仍标记为 Beta
- **最近更新**：最近 3 次提交都是编译/代码清理，无功能性更新
- **活跃度**：**维护不活跃** — 超过 2 年没有实质性功能更新
- **状态**：虽然仍在随引擎更新编译兼容性，但 Epic 似乎已停止积极开发
- **推荐**：对于 ArchViz/产品配置场景仍可使用，但需注意 Beta 标签和可能的限制

⚠️ **警告**：该插件标记为 Beta（`IsBetaVersion=true`），且默认未启用。最近 2 年无功能性更新，仅有编译兼容性修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/VariantManager)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)（Datasmith 文档页，包含 Variant Manager 相关内容）
- [VariantManagerContent 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/VariantManagerContent)（数据类插件）
