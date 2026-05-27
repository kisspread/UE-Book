# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器内容 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

该插件是 Unreal Engine 变体管理器（Variant Manager）系统的**核心数据层**。它定义了用于管理和切换资产、Actor 或组件不同配置（称为“变体”）的核心数据结构，例如 `ULevelVariantSets` 和 `ASwitchActor`。

其主要解决的问题是：在工业可视化、建筑表现、产品配置器等场景中，需要在一个场景内快速切换物体（如材质、位置、可见性）的多种预设状态。本插件提供了这些状态数据的存储、序列化和基础管理功能，而变体管理器编辑器界面则构建于这些数据类之上。

## 使用场景

-   你需要在建筑可视化中，通过一个按钮切换房间的白天/夜晚照明方案。
-   你在为一个汽车品牌做线上配置器，需要实时展示不同颜色、内饰、轮毂的组合。
-   你需要管理一个交互式展示厅中，数十个物体的多种预设状态。

## 蓝图用法

### 核心节点

该插件主要提供数据资产类和基础的工厂类，蓝图中更多是通过“变体管理器”编辑器界面操作这些资产。可直接在蓝图中调用的公开函数较少，主要与资产创建和Actor生成相关。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Level Variant Sets Asset` | 弹出对话框创建一个新的`LevelVariantSets`资产 | `UVariantManagerContentEditorModule` |
| `Create Level Variant Sets Asset (No Dialog)` | 以指定路径和名称创建一个新的`LevelVariantSets`资产 | `UVariantManagerContentEditorModule` |
| `Get Or Create Level Variant Sets Actor` | 获取场景中关联特定资产的`ALevelVariantSetsActor`，若不存在则创建一个 | `UVariantManagerContentEditorModule` |

### 使用示例（蓝图描述）

1.  **在蓝图中创建一个新的 LevelVariantSets 资产**:
    -   使用 `Get Variant Manager Content Editor Module` 节点获取模块实例。
    -   调用其 `Create Level Variant Sets Asset` 方法。这将弹出标准的资产创建对话框。
    -   成功创建后，返回值是新资产的对象引用。
2.  **在场景中生成变体控制 Actor**:
    -   假设你已有一个 `ULevelVariantSets` 资产的引用（例如上一步创建的）。
    -   调用 `Get Variant Manager Content Editor Module` 节点的 `Get Or Create Level Variant Sets Actor` 方法，并传入该资产引用。
    -   如果场景中不存在对应的 `ALevelVariantSetsActor`，该方法会创建一个并返回其引用。

## C++ 用法

主要用法集中在创建和管理 `ULevelVariantSets` 和 `ALevelVariantSetsActor`。

### 头文件引入

```cpp
#include "VariantManagerContentEditorModule.h"
```

### 基本用法

**创建 LevelVariantSets 资产**

```cpp
// 来源：分析自 IVariantManagerContentEditorModule 接口
// 通过模块接口创建资产
IVariantManagerContentEditorModule& VariantManagerModule = IVariantManagerContentEditorModule::Get();
UObject* NewAsset = VariantManagerModule.CreateLevelVariantSetsAsset(
    TEXT("MyVariantSet"), // 资产名称
    TEXT("/Game/Variants"), // 包路径
    true // 是否强制覆盖
);
```

**在场景中获取或生成 Actor**

```cpp
// 假设 LevelVariantSetsAsset 是一个有效的 ULevelVariantSets* 指针
IVariantManagerContentEditorModule& VariantManagerModule = IVariantManagerContentEditorModule::Get();
AActor* VariantActor = VariantManagerModule.GetOrCreateLevelVariantSetsActor(LevelVariantSetsAsset, true);
```

### 进阶用法

**监听变体集编辑器打开事件**

```cpp
// 来源：分析自 IVariantManagerContentEditorModule 接口
// 在某个模块（如你的游戏模块）的 StartupModule 中注册委托
FOnLevelVariantSetsEditor EditorDelegate;
EditorDelegate.BindLambda([](EToolkitMode::Type Mode, const TSharedPtr<IToolkitHost>& Host, ULevelVariantSets* Asset)
{
    UE_LOG(LogTemp, Log, TEXT("VariantManager: Editor opened for asset %s"), *Asset->GetName());
});
IVariantManagerContentEditorModule& VariantManagerModule = IVariantManagerContentEditorModule::Get();
VariantManagerModule.RegisterOnLevelVariantSetsDelegate(EditorDelegate);

// 别忘了在 ShutdownModule 中取消注册
VariantManagerModule.UnregisterOnLevelVariantSetsDelegate();
```

## Demo 示例

以下示例展示如何在自定义的编辑器模块中，监听变体集资产被打开的事件。

**MyEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle OnLevelVariantSetsEditorHandle;
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "VariantManagerContentEditorModule.h"

void FMyEditorModule::StartupModule()
{
    if (IVariantManagerContentEditorModule::IsAvailable())
    {
        IVariantManagerContentEditorModule& VariantManagerModule = IVariantManagerContentEditorModule::Get();
        FOnLevelVariantSetsEditor EditorDelegate;
        EditorDelegate.BindLambda([](EToolkitMode::Type Mode, const TSharedPtr<IToolkitHost>& Host, ULevelVariantSets* Asset)
        {
            if (Asset)
            {
                UE_LOG(LogTemp, Log, TEXT("MyEditorModule: Responding to Variant Set editor open for: %s"), *Asset->GetName());
            }
        });
        OnLevelVariantSetsEditorHandle = VariantManagerModule.RegisterOnLevelVariantSetsDelegate(EditorDelegate);
    }
}

void FMyEditorModule::ShutdownModule()
{
    if (IVariantManagerContentEditorModule::IsAvailable())
    {
        IVariantManagerContentEditorModule& VariantManagerModule = IVariantManagerContentEditorModule::Get();
        VariantManagerModule.UnregisterOnLevelVariantSetsDelegate();
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VariantManager` | 变体管理器编辑器核心逻辑，是本插件编辑器功能（如资产操作）的实际提供者 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复了 LevelVariantSet 中的崩溃问题 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 适配内容浏览器的新“添加”菜单结构 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 处理了 TLazyObjectPtr 废弃警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 自动化可视化的变体管理器小幅更新 |

### 维护评价

-   **创建时间**：该插件创建于 2018 年，是 Unreal Engine 企业功能套件的一部分。
-   **近期更新**：最近的提交（2026年）表明项目仍在维护中，但更新主要是错误修复（崩溃修复）、引擎API适配（废弃标记迁移、日志系统更新）和与其他编辑器功能的集成调整（内容浏览器菜单）。没有重大的新功能添加。
-   **活跃度**：**维护中但不活跃**。作为核心数据模块，其接口已相对稳定，主要工作是确保与引擎最新版本的兼容性。
-   **已知问题/限制**：插件本身标记为 **IsBetaVersion = true**，这意味着其API可能尚未稳定，未来版本可能发生变更。它强依赖于 `VariantManager` 编辑器插件。
-   **推荐使用**：如果你需要在项目中使用变体管理器功能，那么必须启用此插件，因为它提供了基础数据类。但由于其测试版状态，在关键项目中应谨慎使用，并关注版本更新日志。对于大多数场景，直接使用编辑器中的变体管理器界面即可，无需直接引用本插件的C++模块。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)（文档链接指向Datasmith，可能不完全对应）