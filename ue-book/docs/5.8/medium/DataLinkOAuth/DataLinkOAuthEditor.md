# Motion Design Data Link OAuth

> Motion Design Data Link functionality for OAuth 2.0

| 属性 | 值 |
|---|---|
| 中文名 | 数据链OAuth |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DataLinkOAuth` (Runtime), `DataLinkOAuthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLinkOAuth) | |

## 用途

该插件为 **Motion Design Data Link** 框架提供了 **OAuth 2.0** 认证支持。它是一个扩展插件，其核心作用是将复杂的 OAuth 认证流程（如获取访问令牌、刷新令牌）封装成 UE5 可配置的资产和运行时逻辑，以便 Motion Design 的 DataLink 组件能够安全、便捷地访问需要用户授权的第三方 API（例如社交媒体平台、云服务等），获取实时数据用于虚拟制片或广播图形制作。

**它解决的问题是**：使 Motion Design 的数据驱动工作流能够安全地接入需要 OAuth 2.0 授权的外部数据源。

## 使用场景

-   你在使用 Motion Design 工具包制作实时图形，需要从一个需要用户登录授权的 API（例如 Twitter API、Google Sheets API）获取数据并显示在屏幕上。
-   你的虚拟制片场景需要根据一个受 OAuth 保护的云端数据库中的状态来动态改变。
-   你需要将 Unreal 的 Motion Design 数据流安全地连接到企业内部的、采用 OAuth 2.0 协议的 RESTful 服务。

## 蓝图用法

根据提供的源码分析，当前模块主要提供编辑器功能，用于创建和配置 OAuth 设置资产，未直接暴露运行时蓝图函数。

### 核心资产创建流程

| 步骤 | 操作 | 说明 |
|---|---|---|
| 1 | 在内容浏览器中右键 | 展开资产创建菜单 |
| 2 | 选择 `杂项` -> `数据链OAuth设置` | 使用 `UDataLinkOAuthSettingsFactory` 创建资产 |
| 3 | 配置OAuth设置类型 | 在资产详情中选择具体的OAuth提供商设置类（由其他模块提供） |

## C++ 用法

本模块提供了用于创建和管理 OAuth 设置资产的编辑器基础设施。

### 头文件引入

```cpp
#include "DataLinkOAuthSettingsFactory.h"
```

### 基本用法：创建OAuth设置资产工厂

以下示例展示了如何自定义 OAuth 设置资产的创建过程，来源于 `UDataLinkOAuthSettingsFactory`。

```cpp
// 源文件路径: Engine/Plugins/VirtualProduction/DataLinkOAuth/Source/DataLinkOAuthEditor/Private/DataLinkOAuthSettingsFactory.h

// 创建工厂类以生成UDataLinkOAuthSettings资产
UCLASS()
class UDataLinkOAuthSettingsFactory : public UFactory
{
    GENERATED_BODY()

public:
    UDataLinkOAuthSettingsFactory();

    // 覆写UFactory方法以提供自定义行为
    virtual FText GetDisplayName() const override;
    virtual FString GetDefaultNewAssetName() const override;
    virtual uint32 GetMenuCategories() const override;
    virtual bool ConfigureProperties() override; // 可在此处弹出属性配置面板
    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* InContext, FFeedbackContext* InWarn) override;

private:
    // 工厂创建资产时，用于指定具体的OAuth设置子类
    UPROPERTY(EditAnywhere, Category="OAuth")
    TSubclassOf<UDataLinkOAuthSettings> OAuthSettingsClass;
};
```

### 进阶用法：自定义资产显示

以下代码展示了如何定义 OAuth 设置资产在编辑器中的显示方式，来源于 `UAssetDefinition_DataLinkOAuthSettings`。

```cpp
// 源文件路径: Engine/Plugins/VirtualProduction/DataLinkOAuth/Source/DataLinkOAuthEditor/Private/AssetDefinition_DataLinkOAuthSettings.h

// 定义该资产类型在内容浏览器和编辑器中的显示特征
UCLASS()
class UAssetDefinition_DataLinkOAuthSettings : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 覆写方法以自定义资产显示
    virtual FText GetAssetDisplayName() const override; // 资产显示名称
    virtual FLinearColor GetAssetColor() const override; // 资产在内容浏览器中的颜色标识
    virtual TSoftClassPtr<UObject> GetAssetClass() const override; // 关联的资产类
};
```

## Demo 示例

一个演示如何通过工厂创建 OAuth 设置资产的最小 C++ 示例。注意，实际的 `UDataLinkOAuthSettings` 类定义在 `DataLinkOAuth` 运行时模块中。

**OAuthSettingsDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Factories/Factory.h"
#include "DataLinkOAuthSettings.h" // 依赖于DataLinkOAuth模块

// 自定义工厂，用于快速创建特定类型的OAuth设置
class UMyQuickOAuthFactory : public UFactory
{
    GENERATED_BODY()

public:
    UMyQuickOAuthFactory();

    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* InContext, FFeedbackContext* InWarn) override;
    virtual bool CanCreateNew() const override { return true; }
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyFactory", "DisplayName", "快速OAuth设置"); }
};
```

**OAuthSettingsDemo.cpp**
```cpp
#include "OAuthSettingsDemo.h"
#include "DataLinkOAuthSettings.h" // 确保已添加DataLinkOAuth模块依赖

UMyQuickOAuthFactory::UMyQuickOAuthFactory()
{
    // 设置此工厂创建的资产类
    SupportedClass = UDataLinkOAuthSettings::StaticClass();
    bCreateNew = true;
    bEditAfterNew = true;
}

UObject* UMyQuickOAuthFactory::FactoryCreateNew(UClass* InClass, UObject*InParent, FName InName, EObjectFlags InFlags, UObject* InContext, FFeedbackContext* InWarn)
{
    // 创建并返回一个新的UDataLinkOAuthSettings实例
    UDataLinkOAuthSettings* NewSettings = NewObject<UDataLinkOAuthSettings>(InParent, InClass, InName, InFlags);
    // 此处可以为NewSettings设置一些默认参数
    return NewSettings;
}
```

## 模块依赖

从插件的依赖结构和模块类型分析得出。

| 模块 | 用途 |
|---|---|
| `DataLink` | **核心依赖**。提供 DataLink 框架的基础类和接口，OAuth 功能是其认证层扩展。 |
| `DataLinkOAuth` (Runtime) | **本插件运行时模块**。包含 OAuth 认证流程的核心逻辑和设置类（如 `UDataLinkOAuthSettings`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的UE_LOGF格式，属于代码现代化维护。 |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 修复编译问题，在非统一编译模式下显式添加缺失的头文件。 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将包括本插件在内的Motion Design相关插件标记为Beta版。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 首次提交，将插件从实验性目录移至VirtualProduction目录。 |

### 维护评价

该插件**创建时间较新（约1年）**，且**处于Beta版本**。从提交历史看，它最初从实验性目录迁移而来，最近一次实质性更新是8个月前的编译修复和日志更新。作为Beta版本，其API和功能可能不完全稳定。

**结论**：这是一个**处于早期阶段、功能完整的插件**，但标记为Beta。推荐用于Motion Design项目中需要OAuth认证的场景，但需注意其API可能在未来版本中发生变化。目前维护状态尚可，有持续的编译兼容性更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLinkOAuth)
- 官方文档：暂无
- 测试用例：插件目录下未发现专门的测试文件