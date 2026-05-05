# Cinematic Assembly Tools (CAT)

> CAT is a suite of cinematic pipeline tools for shot management and linear content creation

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、命名令牌） |
| 模块 | `CineAssemblyTools` (Runtime), `CineAssemblyToolsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CinematicAssemblyTools) | |

## 用途

Cinematic Assembly Tools (CAT) 是 Epic 为影视制作管线设计的 shot 管理工具套件。它解决的核心问题是：**在大型影视项目中，如何标准化地组织、创建和管理大量 Level Sequence（镜头/片段）资产**。

CAT 的核心抽象是 **Cine Assembly**——一种特殊的 Level Sequence 资产，它不仅包含动画数据，还关联了一个 Level、一个 Schema（模板）、自定义元数据、父子层级关系以及 Production（制作项目）上下文。配合 **Schema**（模板定义）和 **Production Settings**（项目级配置），CAT 允许团队在统一的管线框架下批量创建和管理镜头资产。

### 为什么存在？

- 传统 Sequencer 工作流中，镜头资产的创建和命名是手动的、无组织的
- 影视项目需要统一的帧率、起始帧、子序列优先级等项目级设置
- 需要一种方式将元数据（如镜头号、状态、负责人）附加到每个镜头资产上
- 需要通过 Schema 模板化地批量创建一致的镜头资产和子序列

## 使用场景

- 你在做虚拟制片项目，需要管理数十到数百个镜头 → 用 CAT 的 Production + Assembly 体系
- 你需要为每个镜头标准化元数据（如镜头号、状态、拍摄日期）→ 用 Schema 定义元数据模板
- 你需要批量创建带有子序列的镜头资产（如一个镜头下自动创建 Layout、Animation、FX 子序列）→ 用 Schema 的 SubsequencesToCreate
- 你需要在 Sequencer 中使用命名令牌自动解析镜头名称 → 用 CineAssemblyNamingTokens
- 你需要通过 Take Recorder 录制镜头并自动组织到 Assembly 结构中 → 用 TakeRecorder 集成

## 蓝图用法

CAT 提供了丰富的蓝图接口，主要通过 `UProductionFunctionLibrary` 和 `UCineAssembly` 暴露。

### Production 管理节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Productions` | 获取所有可用的 Cinematic Production | `UProductionFunctionLibrary` |
| `Get Production` | 按 ID 获取特定 Production | `UProductionFunctionLibrary` |
| `Get Active Production` | 获取当前激活的 Production | `UProductionFunctionLibrary` |
| `Set Active Production` | 设置激活的 Production | `UProductionFunctionLibrary` |
| `Clear Active Production` | 清除激活的 Production | `UProductionFunctionLibrary` |
| `Add Production` | 添加新的 Production | `UProductionFunctionLibrary` |
| `Delete Production` | 删除指定 Production | `UProductionFunctionLibrary` |

### Assembly 创建与操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Assembly` | 使用 Schema 和元数据创建新的 CineAssembly | `UProductionFunctionLibrary` |
| `Get Level` | 获取 Assembly 关联的 Level | `UCineAssembly` |
| `Set Level` | 设置 Assembly 关联的 Level | `UCineAssembly` |
| `Get Note Text` / `Set Note Text` | 读写 Assembly 的备注文本 | `UCineAssembly` |
| `Get Parent Assembly` / `Set Parent Assembly` | 读写父 Assembly 引用 | `UCineAssembly` |
| `Get Production ID` / `Get Production Name` | 获取所属 Production 信息 | `UCineAssembly` |

### 元数据节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Metadata As String` | 添加字符串元数据 | `UCineAssembly` |
| `Set Metadata As Bool` | 添加布尔元数据 | `UCineAssembly` |
| `Set Metadata As Integer` | 添加整数元数据 | `UCineAssembly` |
| `Set Metadata As Float` | 添加浮点元数据 | `UCineAssembly` |
| `Set Metadata As Token String` | 添加带令牌的字符串元数据 | `UCineAssembly` |
| `Get Metadata As String` | 读取字符串元数据 | `UCineAssembly` |
| `Get Metadata As Bool` | 读取布尔元数据 | `UCineAssembly` |
| `Get Full Metadata String` | 获取全部元数据的 JSON 字符串 | `UCineAssembly` |

### 使用示例（蓝图描述）

**创建一个 Assembly：**
1. 使用 `Get Active Production` 节点获取当前 Production
2. 使用 `Create Assembly` 节点，传入 Schema 资产引用、目标 Level、父 Assembly（可选）、元数据 Map、路径和名称
3. 返回的 `UCineAssembly` 对象可直接用于 Sequencer 操作

**读取和修改 Assembly 元数据：**
1. 获取 `UCineAssembly` 引用
2. 使用 `Set Metadata As String` 节点，传入 Key（如 "ShotNumber"）和 Value（如 "SH_010"）
3. 使用 `Get Metadata As String` 节点读取回来

## C++ 用法

### 头文件引入

```cpp
#include "CineAssembly.h"
#include "CineAssemblySchema.h"
#include "ProductionSettings.h"
```

### 基本用法

**创建 Assembly 并设置元数据：**

```cpp
// 来源: ProductionFunctionLibrary.cpp - CreateAssembly

// 获取 Schema
UCineAssemblySchema* Schema = /* 你的 Schema 资产 */;

// 创建 CineAssembly (通过 Factory)
UCineAssembly* Assembly = NewObject<UCineAssembly>(GetTransientPackage(), FName("MyAssembly"));
Assembly->SetSchema(Schema);

// 设置关联 Level
Assembly->SetLevel(TSoftObjectPtr<UWorld>(LevelPath));

// 设置元数据
Assembly->SetMetadataAsString(TEXT("ShotNumber"), TEXT("SH_010"));
Assembly->SetMetadataAsBool(TEXT("Approved"), false);
Assembly->SetMetadataAsInteger(TEXT("Take"), 1);
```

**访问 Production 设置：**

```cpp
// 来源: ProductionSettings.h

// 获取 ProductionSettings
UProductionSettings* Settings = GetMutableDefault<UProductionSettings>();

// 获取激活的 Production
FGuid ActiveID = Settings->GetActiveProductionID();
TOptional<const FCinematicProduction> Production = Settings->GetActiveProduction();

// 获取帧率和起始帧
FFrameRate DisplayRate = Settings->GetActiveDisplayRate();
int32 StartFrame = Settings->GetActiveStartFrame();
```

### 进阶用法

**注册 Production 扩展数据：**

```cpp
// 来源: ICineAssemblyToolsEditorModule.h

// 定义自定义扩展结构
USTRUCT()
struct FMyProductionExtension
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = Default)
    FString CustomField;
};

// 注册扩展
ICineAssemblyToolsEditorModule& Module = ICineAssemblyToolsEditorModule::Get();
Module.RegisterProductionExtension(*FMyProductionExtension::StaticStruct());

// 访问扩展数据
UProductionSettings* Settings = GetMutableDefault<UProductionSettings>();
TConstStructView<FMyProductionExtension> Data = Settings->GetProductionExtendedData<FMyProductionExtension>(ProductionID);
```

**使用命名令牌解析 Assembly 名称：**

```cpp
// 来源: CineAssemblyNamingTokens.h

// 解析包含令牌的字符串
FText Resolved = UCineAssemblyNamingTokens::GetResolvedText(
    TEXT("{cineassembly.shotname}_v{cineassembly.version}"),
    MyAssembly
);
```

## Demo 示例

### 最小可编译示例：创建 Assembly 并设置元数据

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "CineAssemblyTools",
    "LevelSequence",
    "NamingTokens",
});
```

**MyAssemblyHelper.h:**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "CineAssembly.h"
#include "CineAssemblySchema.h"

class FMyAssemblyHelper
{
public:
    // 创建一个 Assembly 并添加元数据
    static UCineAssembly* CreateShotAssembly(
        UCineAssemblySchema* InSchema,
        TSoftObjectPtr<UWorld> InLevel,
        const FString& InName,
        const FString& InShotNumber);

    // 读取 Assembly 的元数据
    static bool GetShotNumber(UCineAssembly* Assembly, FString& OutShotNumber);
};
```

**MyAssemblyHelper.cpp:**
```cpp
#include "MyAssemblyHelper.h"

UCineAssembly* FMyAssemblyHelper::CreateShotAssembly(
    UCineAssemblySchema* InSchema,
    TSoftObjectPtr<UWorld> InLevel,
    const FString& InName,
    const FString& InShotNumber)
{
    // 创建 Assembly
    UCineAssembly* Assembly = NewObject<UCineAssembly>(
        GetTransientPackage(), FName(*InName));

    // 设置 Schema（定义元数据模板和子序列）
    Assembly->SetSchema(InSchema);

    // 设置关联 Level
    Assembly->SetLevel(InLevel);

    // 设置自定义元数据
    Assembly->SetMetadataAsString(TEXT("ShotNumber"), InShotNumber);
    Assembly->SetMetadataAsBool(TEXT("IsApproved"), false);

    return Assembly;
}

bool FMyAssemblyHelper::GetShotNumber(UCineAssembly* Assembly, FString& OutShotNumber)
{
    if (!Assembly)
    {
        return false;
    }
    return Assembly->GetMetadataAsString(TEXT("ShotNumber"), OutShotNumber);
}
```

## 模块依赖

### CineAssemblyTools (Runtime)

| 模块 | 用途 |
|---|---|
| `Engine` | 核心引擎功能 |
| `LevelSequence` | Level Sequence 基础设施 |
| `NamingTokens` | 命名令牌系统，用于模板化名称解析 |
| `Core` | 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Json` | JSON 解析（元数据序列化） |
| `JsonUtilities` | JSON 工具函数 |
| `MovieScene` | Sequencer 底层场景图 |
| `SlateCore` | Slate UI 核心 |
| `UniversalObjectLocator` | 对象定位器 |

### CineAssemblyToolsEditor (Editor)

| 模块 | 用途 |
|---|---|
| `CineAssemblyTools` | 依赖 Runtime 模块 |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `TakeRecorder` | Take Recorder 集成 |
| `TakesCore` | Takes 核心功能 |
| `MovieRenderPipelineCore` | 渲染管线集成 |
| `NamingTokens` | 命名令牌系统 |
| `DirectoryPlaceholder` | 目录占位符工具 |
| `AssetDefinition` | 资产类型定义 |
| `AssetTools` | 资产工具 |
| `PropertyEditor` | 属性编辑器自定义 |
| `SourceControl` | 版本控制集成 |
| `UnrealEd` | 编辑器核心 |

## 子模块文档

| 模块 | 类型 | 说明 |
|---|---|---|
| [CineAssemblyTools](CineAssemblyTools.md) | Runtime | 核心运行时模块：Assembly、Schema、NamingTokens |
| [CineAssemblyToolsEditor](CineAssemblyToolsEditor.md) | Editor | 编辑器模块：Production 设置、UI、TakeRecorder 集成 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-14 | `77dbb90e` | 修复 Assembly 字符串元数据中令牌重复评估的问题，改为存储未解析和已解析两种文本，支持手动重新评估 |
| 2025-10-03 | `096beboe` | 修复 Schema 和 Assembly 窗口在用户切换到其他 UE 窗口时被最小化的问题 |
| 2025-10-03 | `5588f066` | 修复 Cine Assembly 在设置 Schema 时未自动添加元数据令牌的问题 |

### 维护评价

- **创建时间**：2025-04-23，是一个较新的插件（约 1 年）
- **更新频率**：2025 年 10 月有密集的 bug 修复更新，说明处于活跃开发阶段
- **活跃程度**：活跃维护中，持续有功能性修复和改进
- **实验性标记**：`IsExperimentalVersion=true`，尚未标记为正式版本
- **已知限制**：作为实验性插件，API 可能在未来版本中发生变化
- **推荐程度**：如果你的项目是虚拟制片/影视制作管线，强烈推荐关注；但注意实验性状态，生产环境使用需谨慎

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CinematicAssemblyTools)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CinematicAssemblyTools)（暂未发现独立测试目录）
