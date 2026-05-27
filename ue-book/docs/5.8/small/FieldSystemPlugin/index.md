# Field System

> Analytic Field

| 属性 | 值 |
|---|---|
| 中文名 | 场系统 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（场系统资产） |
| 模块 | `FieldSystemEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-12-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FieldSystemPlugin) | |

## 用途

该插件为 Unreal Engine 提供了 **“场系统（Field System）”** 资产的编辑器支持。它主要解决如何在编辑器中创建和管理“场”资产的问题。这里的“场”（Field）通常用于定义空间中的向量、标量或整型值分布，常用于 Chaos 物理系统（如破碎模拟）中定义影响区域、衰减规则或空间约束。插件的核心是作为编辑器扩展，为 `UFieldSystem` 资产提供工厂、资产类型操作和编辑器样式。

## 使用场景

- 你在使用 **Chaos 物理系统** 进行高级破碎模拟，需要定义力场、速度场或衰减场来控制破碎效果时。
- 你需要为**程序化几何体**或**粒子系统**创建基于空间坐标的值分布规则时。

## 蓝图用法

该插件主要为编辑器提供资产创建与管理界面，公开的运行时蓝图 API 较少。

### 核心节点

从提供的源码分析，未发现直接暴露给蓝图的 `BlueprintCallable` 函数。该插件的功能主要通过编辑器资产操作（如右键创建新资产）来使用。

### 使用示例（蓝图描述）

在内容浏览器中：
1. 右键 -> 物理 -> **Field System**。
2. 创建一个新的 Field System 资产。
3. 双击打开该资产，在专门的场编辑器中进行配置（具体配置方式属于运行时场系统功能，不在此编辑器插件范围内）。

## C++ 用法

该插件的主要用法体现在其提供的资产工厂上，用于在代码中程序化创建 Field System 资产。

### 头文件引入

```cpp
#include "Field/FieldSystemFactory.h"
```

### 基本用法

通过插件提供的 `UFieldSystemFactory` 来创建 Field System 资产。
*代码示例参考自 `FieldSystemFactory.h`*

```cpp
// 创建一个新的 Field System 资产
UFieldSystem* NewFieldSystem = UFieldSystemFactory::StaticFactoryCreateNew(
    UFieldSystem::StaticClass(),
    MyOuterObject, // 外部对象（如一个包）
    FName(“MyNewFieldSystem”), // 资产名称
    RF_NoFlags, // 对象标志
    nullptr, // 上下文
    GWarn // 反馈上下文（警告）
);
```

## Demo 示例

一个简单的示例，展示如何在运行时通过 C++ 获取插件模块。

### FieldSystemDemoActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FieldSystemDemoActor.generated.h"

UCLASS()
class AFieldSystemDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AFieldSystemDemoActor();

    virtual void BeginPlay() override;

private:
    void CheckFieldSystemEditorModule();
};
```

### FieldSystemDemoActor.cpp
```cpp
#include "FieldSystemDemoActor.h"
#include "Field/FieldSystemEditorModule.h"

AFieldSystemDemoActor::AFieldSystemDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AFieldSystemDemoActor::BeginPlay()
{
    Super::BeginPlay();
    CheckFieldSystemEditorModule();
}

void AFieldSystemDemoActor::CheckFieldSystemEditorModule()
{
    // 检查 FieldSystemEditor 模块是否已加载并可用
    if (IFieldSystemEditorModule::IsAvailable())
    {
        // 获取模块单例（注意：通常在编辑器环境下可用）
        IFieldSystemEditorModule& FieldSystemEditor = IFieldSystemEditorModule::Get();
        UE_LOG(LogTemp, Log, TEXT("FieldSystemEditor module is available."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("FieldSystemEditor module is not available."));
    }
}
```

## 模块依赖

该插件仅包含一个模块 `FieldSystemEditor`，且没有列出额外的依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了链接器中的重复符号错误 |
| 2023-11-15 | `b64f2e25` | [Deprecation Cleanup] Remove deprecated code in actor factory class | 清理了 Actor 工厂类中的已废弃代码 |
| 2023-02-17 | `73c74eaf` | Removing redundant include paths: | 移除了冗余的包含路径 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 通用的插件目录更新 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接更新为安全协议 |

### 维护评价

- **年龄**：插件创建于 2018 年，已超过 7 年，属于“老古董”。
- **维护频率**：更新频率较低，最后一次功能性更新（符号修复）发生在 2026 年初，之前两年主要是编译和代码清理。
- **维护状态**：**低活跃度维护**。插件仍被纳入主仓库构建，没有被标记为废弃，但功能上已趋于稳定，没有新功能的开发迹象。
- **已知限制**：作为实验性插件，且 `EnabledByDefault=false`，它不是一个开箱即用的功能，需要用户主动启用。
- **推荐使用**：**谨慎推荐**。如果你需要在使用 Chaos 等高级物理系统时进行场定义，并且不介意使用实验性插件，可以尝试。否则，对于大多数项目，可等待其正式发布或寻找替代方案。使用时需注意其实验性状态和可能的未来变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FieldSystemPlugin)
- [官方文档]() (无)
- [测试用例]() (提供的文件信息中未发现测试用例，可在 `Engine/Tests/` 目录下搜索相关关键词)