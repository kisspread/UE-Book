# DMX Modular Features

> Modular Features for DMX

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction (Misc) |
| 默认启用 | 是 |
| 包含内容 | 是 |
| 模块 | DMXFixtureActorInterface (Runtime) |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures) | |

## 用途

DMXModularFeatures 是一个极轻量级的接口插件，为 DMX 系统提供 **MVR Fixture Actor 接口**。它只定义了一个 `UInterface`，让 Actor 能够被 MVR（My Virtual Rig）工作流识别为 DMX Fixture。

这个插件存在的原因是 **模块解耦**：DMXEngine 和 DMXFixtures 都需要知道"哪些 Actor 是 MVR Fixture"，但不应该互相强依赖。通过提取这个接口到独立插件，各模块可以松耦合地引用同一接口。

插件标记为 `Hidden: true`，用户不会在插件浏览器中看到它——它作为内部基础设施自动被其他 DMX 插件依赖。

### 核心接口：IDMXMVRFixtureActorInterface

当一个 Actor 实现此接口后，MVR 场景导入/导出流程会将其识别为 MVR Fixture Actor，并在自动选择 Fixture 时予以考虑。

**前提条件**：实现此接口的 Actor 必须恰好有一个 `DMXComponent` 子对象。DMXComponent 会将自己的 MVR UUID 写入 Actor 的 MetaData，从而使 Actor 被识别为 MVR Actor。

## 使用场景

- 你在使用 DMX 虚拟制作系统，需要让自定义 Actor 参与 MVR 工作流 → 实现此接口
- 你正在开发自定义 DMX Fixture Actor，希望它能被 MVR 场景正确识别和管理 → 实现此接口
- 你正在编写 MVR 导入/导出工具，需要查询 Actor 支持哪些 DMX 属性 → 调用此接口的方法

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `On MVR Get Supported DMX Attributes` | 返回该 Actor 支持的 DMX 属性名和矩阵属性名 | `IDMXMVRFixtureActorInterface` |

### 使用示例（蓝图描述）

1. 创建一个继承 Actor 的蓝图类
2. 在蓝图类设置中添加 `DMXComponent` 作为子组件
3. 在蓝图类的 Class Settings → Interfaces 中添加 `DMXMVRFixtureActorInterface`
4. 实现 `On MVR Get Supported DMX Attributes` 事件：
   - 从 `OutAttributeNames` 输出引脚返回支持的 DMX 属性名（如 `Color`, `Intensity` 等）
   - 从 `OutMatrixAttributeNames` 输出引脚返回支持的矩阵属性名（如像素映射属性）

## C++ 用法

### 头文件引入

```cpp
#include "DMXMVRFixtureActorInterface.h"
```

### 基本用法

让自定义 Actor 实现 `IDMXMVRFixtureActorInterface` 接口：

```cpp
// MyFixtureActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "DMXMVRFixtureActorInterface.h"
#include "MyFixtureActor.generated.h"

UCLASS()
class AMyFixtureActor : public AActor, public IDMXMVRFixtureActorInterface
{
    GENERATED_BODY()

public:
    AMyFixtureActor();

    // IDMXMVRFixtureActorInterface
    virtual void OnMVRGetSupportedDMXAttributes_Implementation(
        TArray<FName>& OutAttributeNames,
        TArray<FName>& OutMatrixAttributeNames) const override;
};
```

```cpp
// MyFixtureActor.cpp
#include "MyFixtureActor.h"
#include "Components/DMXComponent.h"

AMyFixtureActor::AMyFixtureActor()
{
    // 必须恰好有一个 DMXComponent
    auto* DMXComp = CreateDefaultSubobject<UDMXComponent>(TEXT("DMXComponent"));
}

void AMyFixtureActor::OnMVRGetSupportedDMXAttributes_Implementation(
    TArray<FName>& OutAttributeNames,
    TArray<FName>& OutMatrixAttributeNames) const
{
    // 声明此 Actor 支持的 DMX 属性
    OutAttributeNames.Add(FName("Color"));
    OutAttributeNames.Add(FName("Intensity"));
    OutAttributeNames.Add(FName("Pan"));
    OutAttributeNames.Add(FName("Tilt"));

    // 矩阵属性（用于像素化 Fixture）
    // OutMatrixAttributeNames.Add(FName("PixelColor"));
}
```

### 进阶用法：运行时查询接口

在 MVR 导入流程中，引擎会通过 `Cast` 检查 Actor 是否实现了此接口，并通过 `Execute_OnMVRGetSupportedDMXAttributes` 获取支持的属性列表：

```cpp
// 检查 Actor 是否为 MVR Fixture
if (IDMXMVRFixtureActorInterface* MVRFixtureActor = Cast<IDMXMVRFixtureActorInterface>(SomeActor))
{
    // 获取支持的 DMX 属性
    TArray<FName> SupportedAttributes;
    TArray<FName> SupportedMatrixAttributes;
    IDMXMVRFixtureActorInterface::Execute_OnMVRGetSupportedDMXAttributes(
        SomeActor, SupportedAttributes, SupportedMatrixAttributes);

    // 处理属性列表...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统，提供 UInterface 支持 |

使用者无需在自己的 Build.cs 中依赖 `DMXFixtureActorInterface`——该模块是 Runtime 类型，会在引擎启动时自动加载。但如果你想在 C++ 中直接 `#include` 此头文件，需要添加依赖：

```csharp
PublicDependencyModuleNames.Add("DMXFixtureActorInterface");
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2024-09-17 | `46920085c27d` | 移除 DMX 插件的 experimental 和 beta 标记，DMX 全部插件正式标记为 production ready |
| 2024-03-28 | `d827381eb619` | 修正 Build.cs 文件名大小写（第 2 部分） |
| 2024-03-28 | `02c97c2719c0` | 修正 Build.cs 文件名大小写（第 1 部分） |

### 维护评价

- **创建时间**：2022 年 9 月，约 3.5 年历史
- **更新频率**：极低——该插件自创建以来几乎没有功能性改动，最近的 commit 都是维护性调整（大小写修正、移除 beta 标记）
- **维护状态**：稳定/不活跃。作为纯接口定义，代码量极少且不需要频繁更新，这是正常的
- **已知限制**：无文档 URL、无测试用例
- **推荐使用**：✅ 推荐。这是 DMX/MVR 工作流的标准接口，如果你在开发 DMX Fixture Actor，应当实现此接口。该接口自 2024 年已标记为 production ready

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures)
- [DMXFixtureActor 实现示例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/DMX/DMXFixtures/Source/DMXFixtures/Public/DMXFixtureActor.h) — 内置 Fixture Actor 实现了此接口
- [MVR Scene Actor 使用示例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXRuntime/Private/MVR/DMXMVRSceneActor.cpp) — MVR 场景中 Cast 检查接口
- [MVR Fixture Actor Library](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXRuntime/Private/MVR/DMXMVRFixtureActorLibrary.cpp) — 通过接口查询支持的属性
