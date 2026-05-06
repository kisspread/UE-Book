# Field System

> Analytic Field

| 属性 | 值 |
|---|---|
| 中文名 | 场系统 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资源、缩略图、资产类型动作） |
| 模块 | `FieldSystemEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FieldSystemPlugin) | |

## 用途

Field System 插件为 UE5 的 **解析场（Analytic Field）** 系统提供编辑器支持。解析场是 Chaos 物理系统的一部分，用于定义基于数学函数的空间物理量（如力、速度、密度等），常用于程序化破坏、柔体模拟、风场控制等场景。该插件本身**不包含运行时逻辑**，而是提供了：

- 在内容浏览器中创建和管理 `UFieldSystem` 资产
- 资产缩略图与图标
- 将场资产拖放到场景中生成 Actor 的工厂机制
- 编辑器模块的注册与生命周期管理

> **注意**：此插件已标记为 Beta 版本，默认不启用，需手动在插件设置中开启。

## 使用场景

- **Chaos 物理模拟**：当你需要为刚体或柔体施加基于解析场的力（如爆炸、漩涡、气流）时，需要先创建 `UFieldSystem` 资产，然后通过 Chaos 的场节点或蓝图使用。
- **程序化生成**：利用场定义自定义的变形或分布规则，结合 Niagara 或几何脚本使用。
- **编辑器开发**：若需要扩展场系统的编辑器功能，此插件提供了资产类型注册、工厂、样式等基础框架。

## 蓝图用法

该插件**不暴露任何 BlueprintCallable 函数**，纯编辑器插件。运行时场逻辑由 Chaos 模块提供（如 `ChaosSolverEngine` 等），不在本插件范围内。

## C++ 用法

### 头文件引入

```cpp
#include "Field/FieldSystem.h"
#include "Field/FieldSystemAsset.h"
#include "FieldSystemEditorModule.h"
```

### 基本用法

由于该插件是编辑器模块，其典型用法是在 C++ 编辑器模块中注册新资产类型的快捷方式。以下摘自官方测试代码：创建 `UFieldSystem` 资产并保存。

```cpp
// 来源：Engine/Plugins/Experimental/FieldSystemPlugin/Source/FieldSyStemEditor/Private/Field/FieldSystemFactory.cpp
UFieldSystem* NewField = UFieldSystemFactory::StaticFactoryCreateNew(
    UFieldSystem::StaticClass(),
    GetTransientPackage(),
    FName(TEXT("MyFieldSystem")),
    RF_Standalone | RF_Public,
    nullptr,
    GWarn
);
```

### 进阶用法

在编辑器模块启动时注册资产类型动作，使内容浏览器支持 `UFieldSystem`：

```cpp
// 来源：Engine/Plugins/Experimental/FieldSystemPlugin/Source/FieldSyStemEditor/Private/FieldSystemEditorModule.cpp
void IFieldSystemEditorModule::StartupModule()
{
    // 注册资产类型动作
    AssetTypeActions_FieldSystem = new FAssetTypeActions_FieldSystem();
    FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get().RegisterAssetTypeActions(AssetTypeActions_FieldSystem->AsShared());
}
```

## Demo 示例

由于该插件不包含运行时逻辑，无法提供完整的可执行游戏 Demo。以下为创建一个 `UFieldSystem` 资产的编辑器工具示例（C++，需在编辑器模块中运行）。

**MyFieldCreator.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Field/FieldSystem.h"

class FMyFieldCreator
{
public:
    static UFieldSystem* CreateFieldAsset();
};
```

**MyFieldCreator.cpp**

```cpp
#include "MyFieldCreator.h"
#include "Field/FieldSystemFactory.h"
#include "Misc/PackageName.h"

UFieldSystem* FMyFieldCreator::CreateFieldAsset()
{
    // 使用工厂创建在场包中的资产
    UPackage* Package = CreatePackage(*FString::Printf(TEXT("/Game/MyFields/MyField_%d"), FMath::Rand()));
    UFieldSystem* NewField = UFieldSystemFactory::StaticFactoryCreateNew(
        UFieldSystem::StaticClass(),
        Package,
        FName(TEXT("MyField")),
        RF_Standalone | RF_Public | RF_Transactional,
        nullptr,
        GWarn
    );
    if (NewField)
    {
        // 保存资产
        FAssetRegistryModule::AssetCreated(NewField);
        NewField->MarkPackageDirty();
    }
    return NewField;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/UnrealEd 等） | - |

该插件仅依赖引擎标准编辑器模块（如 `UnrealEd`, `AssetTools`, `Slate`），无需额外第三方库。

## 维护状态

### 近期更新

- 2023-11-15 `b64f2e25` [Deprecation Cleanup] Remove deprecated code in actor factory class
- 2023-02-17 `73c74eaf` Removing redundant include paths
- 2023-01-16 `bbc37aa2` [Engine/Plugins] General plugin maintenance
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol
- 2022-05-02 `d64cf417` AssetRegistry includes (Engine Plugins): change #include "AssetData.h" -> #include "AssetRegistry/AssetData.h"

### 维护评价

- **创建时间**：2022-05-02（约 3 年前）
- **最近更新**：2023-11-15，至今已超过 1 年无实质性功能更新（仅清理弃用代码）。
- **活跃度**：不活跃，未来可能不再维护。
- **已知问题**：标记为 Beta，可能存在稳定性问题；插件默认关闭，需要手动启用。
- **推荐使用**：如果项目需要使用 Chaos 场系统，建议启用此插件以便在编辑器中创建和管理场资产。对于纯代码项目，也可以绕过此插件直接使用运行时场 API。

> ⚠️ 警告：自 2023 年 11 月以来无功能更新，且仍为 Beta 版本，请在项目中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FieldSystemPlugin)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/chaos-physics/fields/)（Chaos 场系统概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FieldSystemPlugin/Source/FieldSyStemEditor)（源码目录即包含构建和测试）