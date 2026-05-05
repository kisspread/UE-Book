# Asset Referencing Restrictions

> Apply project-specific restrictions to how content in different folders or plugins can be referenced

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AssetReferenceRestrictions (Editor) |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetReferenceRestrictions) | |

## 用途

AssetReferenceRestrictions 是一个**编辑器插件**，用于在项目中实施资产引用的**域（Domain）隔离策略**。它解决的核心问题是：**防止不同模块/插件的资产之间发生不受控的交叉引用**。

在大型项目中（尤其是采用 Game Feature Plugin 架构的项目），不同插件之间的资产依赖关系如果不受管理，会导致：
- 打包时引入不需要的内容，增大包体
- 插件无法独立部署或热更新
- 难以维护模块边界

该插件通过"域"（Domain）的概念将资产划分为不同的可见性区域，限制哪些域可以引用哪些域的资产。违反规则时，会在资产验证（Data Validation）中报告错误，同时在编辑器的资产选择器（Asset Picker）中过滤掉不允许引用的资产。

插件依赖 `DataValidation` 插件，内置了两个验证器自动检测违规引用。

## 使用场景

- **Game Feature Plugin 架构**：你的项目使用 GameFeature 插件做模块化内容，需要确保 GameFeature 插件之间不能随意互相引用资产，只能通过声明依赖来访问
- **大型团队协作**：多个团队分别负责不同插件/模块，需要防止无意中引用了不属于自己的资产
- **包体优化**：希望确保某些内容域（如 Cinematic、Debug 资产）不会被游戏运行时代码引用
- **自定义域隔离**：项目中有特定文件夹（如 `/Game/Prototype/`）不允许被正式游戏内容引用

## 配置方法

### 启用插件

在 `DefaultEngine.ini` 或编辑器的 Plugins 面板中启用 `AssetReferenceRestrictions`（默认未启用）。

### 设置入口

设置位于 **Project Settings → Asset Referencing Policy**，对应的配置类为 `UAssetReferencingPolicySettings`（`config=Game`）。

### 配置结构概览

```
Asset Referencing Policy
├── Engine Plugins          ← 引擎插件的域规则
│   ├── DefaultRule
│   │   ├── CanReferenceTheseDomains
│   │   ├── bCanProjectAccessThesePlugins
│   │   └── bCanBeSeenByOtherDomainsWithoutDependency
│   └── AdditionalRules[]   ← 按路径/分类匹配的规则
├── Project Plugins         ← 项目插件的域规则（结构同上）
├── Project Content         ← /Game/ 目录的域规则
│   ├── DefaultRule
│   │   └── CanReferenceTheseDomains
│   └── AdditionalDomains[] ← 自定义域定义
│       ├── DomainName
│       ├── ContentRoots[]
│       ├── SpecificAssets[]
│       ├── ReferenceMode
│       └── CanReferenceTheseDomains[]
├── AdditionalDomains       ← 从项目内容中划出的额外域
└── bIgnoreEditorOnlyReferences ← 是否忽略仅编辑器的引用（默认 true）
```

### 默认行为

插件的默认构造函数（`UAssetReferencingPolicySettings`）设置了以下默认规则：

- **GameFeature 插件**自动匹配路径前缀 `/GameFeatures/`，可引用 `ProjectContent` 域
- **引擎插件**默认可被其他域看到（`bCanBeSeenByOtherDomainsWithoutDependency = true`）
- **项目插件**默认可引用 `ProjectContent` 域
- **ProjectContent** 始终可看到 `EngineContent`

### 内置域

系统自动创建以下内置域：

| 域名 | 内容 | 说明 |
|---|---|---|
| `EngineContent` | `/Engine/` | 引擎内置资产，所有域都可见 |
| `ProjectContent` | `/Game/` | 项目主内容 |
| `Script` | `/Script/` | 反射类型，完全不受限制 |
| `Temp` | `/Temp/`, `/Memory/`, `/Extra/` | 临时内容，完全不受限制 |
| `NeverCook` | 从 Packaging Settings 的 DirectoriesToNeverCook 获取 | 永不打包的内容，不受限制 |

### 插件匹配规则

每个插件会被自动识别为一个域。匹配规则时的优先级：

1. **最具体的路径匹配**（最长前缀）
2. 任意路径匹配
3. **最具体的分类匹配**（最长前缀）
4. 任意分类匹配

插件也可以通过 `.uplugin` 中的 `Plugins` 数组声明依赖，被依赖的插件域自动对依赖者可见。

### 控制台变量

```
AssetReferencingPolicy.CheckForMissingRefsToExternalActors 1
```

启用后，验证时也会检测对不存在的 External Actor 的引用（默认关闭）。

### 调试命令

```
Editor.AssetReferenceRestrictions.ListDomainDatabase
```

在 Output Log 中打印所有已知域及其可见性关系，便于排查配置问题。

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 接口。它是纯编辑器插件，所有功能通过 Project Settings 配置和 Data Validation 系统自动生效。

## C++ 用法

该插件为 Editor 模块，不提供运行时 API。但可以通过 C++ 查询域数据库和验证资产引用。

### 头文件引入

```cpp
#include "AssetReferencingPolicySubsystem.h"
#include "AssetReferencingDomains.h"
#include "AssetReferencingPolicySettings.h"
```

### 查询某个资产是否受引用限制

```cpp
// 获取子系统
UAssetReferencingPolicySubsystem* Subsystem = GEditor->GetEditorSubsystem<UAssetReferencingPolicySubsystem>();

// 检查某个资产的引用是否需要被验证
FAssetData AssetData; // 从 AssetRegistry 获取
bool bNeedsValidation = Subsystem->ShouldValidateAssetReferences(AssetData);
```

### 验证某个资产的所有引用

```cpp
UAssetReferencingPolicySubsystem* Subsystem = GEditor->GetEditorSubsystem<UAssetReferencingPolicySubsystem>();
FAssetData AssetData = /* ... */;

TValueOrError<void, TArray<FAssetReferenceError>> Result = Subsystem->ValidateAssetReferences(AssetData);

if (Result.HasError())
{
    for (const FAssetReferenceError& Error : Result.GetError())
    {
        // Error.Type: DoesNotExist (资产不存在) 或 Illegal (违反域策略)
        // Error.Message: 用户可读的错误信息
        // Error.ReferencedAsset: 被引用的资产
        // Error.bTreatErrorAsWarning: 是否降级为警告
        UE_LOG(LogTemp, Warning, TEXT("%s"), *Error.Message.ToString());
    }
}
```

### 直接操作域数据库

```cpp
TSharedPtr<FDomainDatabase> DomainDB = Subsystem->GetDomainDB();

// 查找某个资产所属的域
TSharedPtr<FDomainData> Domain = DomainDB->FindDomainFromAssetData(AssetData);

// 检查两个域之间是否可以互相引用
TSharedPtr<FDomainData> SourceDomain = /* ... */;
TSharedPtr<FDomainData> TargetDomain = /* ... */;
auto [bCanSee, ErrorText] = DomainDB->CanDomainsSeeEachOther(TargetDomain, SourceDomain);
```

### 获取配置设置

```cpp
const UAssetReferencingPolicySettings* Settings = GetDefault<UAssetReferencingPolicySettings>();

// 访问引擎插件规则
const FARPDomainSettingsForPlugins& EngineRules = Settings->EnginePlugins;

// 访问项目插件规则
const FARPDomainSettingsForPlugins& ProjectRules = Settings->ProjectPlugins;

// 访问自定义域列表
for (const FARPDomainDefinitionByContentRoot& Domain : Settings->AdditionalDomains)
{
    // Domain.DomainName, Domain.ContentRoots, Domain.ReferenceMode, ...
}
```

### 自定义域过滤器

```cpp
// FDomainAssetReferenceFilter 是 IAssetReferenceFilter 的实现
// 它会在 AssetPicker 中自动过滤不允许引用的资产
// 如需手动创建：
FAssetReferenceFilterContext Context;
Context.AddReferencingAsset(MyAssetData);
TSharedPtr<IAssetReferenceFilter> Filter = GEditor->MakeAssetReferenceFilter(Context);

// 在自定义 UI 中使用
FText FailureReason;
bool bPasses = Filter->PassesFilter(CandidateAssetData, &FailureReason);
```

## Demo 示例

### 最小配置：为项目内容添加自定义域

假设你想把 `/Game/Cinematics/` 目录隔离出来，不允许游戏运行时代码引用它：

**1. 在 Project Settings → Asset Referencing Policy → Project Content → AdditionalDomains 中添加：**

| 字段 | 值 |
|---|---|
| DomainName | `Cinematics` |
| DomainDisplayName | `Cinematic Content` |
| ErrorMessageIfUsedElsewhere | `Cinematic content should not be referenced by runtime game assets` |
| ContentRoots | `/Game/Cinematics/` |
| ReferenceMode | `AdditionalDomains` (默认) |
| CanReferenceTheseDomains | (留空，表示该域只能看到 EngineContent 和自己) |

**2. 效果：**
- `/Game/Cinematics/` 下的资产被隔离为独立域
- 游戏代码（ProjectContent 域）试图引用 Cinematics 域的资产时，资产验证会报错
- 编辑器中从游戏资产选择引用时，Cinematics 域的资产会被过滤掉

### GameFeature 插件隔离（开箱即用）

插件默认已经为 `/GameFeatures/` 路径下的插件配置了规则：
- 每个 GameFeature 插件自动成为一个独立域
- 只能引用 `ProjectContent` 和 `EngineContent`
- 其他插件必须在 `.uplugin` 中声明依赖才能访问其内容

无需额外配置即可生效。

## 模块依赖

从 `AssetReferenceRestrictions.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |

**注意**：该插件为 Editor-only 模块，不可在运行时使用。如果你的模块需要调用其 API，需要在 `.Build.cs` 中添加对 `AssetReferenceRestrictions` 的依赖，且你的模块也必须是 Editor 类型。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e7518` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 编译优化，为有对应 .gen.cpp 的源文件添加内联宏 |
| 2025-05-30 | `8396b18` | Updated headers for dllstorage | 代码规范化，将 DLL export 标记从类型移到方法/静态变量上 |
| 2025-04-11 | `a4cc4fd` | Make missing external actor ref validation independent of classification | 功能改进：External Actor 引用验证不再依赖 hard/soft/game/editoronly 分类 |

### 维护评价

- **创建时间**：2021-03-23，约 5 年历史
- **最近更新**：2025-06-26，3 个月内有更新
- **活跃程度**：**活跃维护中**。近期更新主要是代码规范化和功能改进，说明 Epic 在持续维护
- **稳定性**：作为编辑器基础设施插件，API 比较稳定，无废弃标记
- **推荐使用**：✅ 推荐。对于采用 Game Feature Plugin 架构或多插件模块化的项目，该插件是强制执行资产边界的重要工具。即使用默认配置，也能自动为 GameFeature 插件提供隔离保护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetReferenceRestrictions)
- 官方文档：无（.uplugin 的 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetReferenceRestrictions/Tests)：插件目录下未包含独立测试文件
