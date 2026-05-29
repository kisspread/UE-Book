# DMX Modular Features

> Modular Features for DMX（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX模块化功能 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXFixtureActorInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures) | |

## 用途

该插件提供了一个标准的接口（`IDMXMVRFixtureActorInterface`），其核心作用是**解耦**。它允许任意Actor（例如由设计师在蓝图中创建的复杂场景道具）实现一个接口，从而被MVR（可能是某种灯光管理系统或工具）自动识别为一个DMX Fixture（灯光设备）。

通过这个接口，MVR系统可以查询该Actor支持的DMX属性列表，而无需Actor本身或MVR系统直接依赖完整的DMX插件。实现了功能的模块化和标准化集成。

## 使用场景

- 当你创建了一个自定义的蓝图Actor，例如一个舞台上的动态雕塑，并希望它也能被DMX灯光控制系统的MVR工具（如Vectorworks）识别和控制时。
- 当你需要让一个不是专门用于DMX控制的Actor，能够被MVR系统发现，并暴露其支持的DMX属性时，可以实现此接口。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `On MVR Get Supported DMX Attributes` | 供MVR系统调用，获取此Actor支持的DMX属性名称和矩阵属性名称列表。 | `IDMXMVRFixtureActorInterface` |

### 使用示例（蓝图描述）

1.  打开你的蓝图Actor（例如`BP_MyLamp`）。
2.  在蓝图类设置中，添加接口 `DMXMVRFixtureActorInterface`。
3.  在“我的蓝图”面板的“接口”下，覆写（Override）函数 `On MVR Get Supported DMX Attributes`。
4.  在该函数的图表中，你需要填充两个输出引脚：
    - `Out Attribute Names`: 填充该Actor支持的常规DMX属性（如`Color`, `Intensity`）的名称数组。
    - `Out Matrix Attribute Names`: 填充该Actor支持的矩阵/像素DMX属性（如`MatrixPixelColor`）的名称数组。
    - 例如，你可以创建一个本地变量数组，填入`FName`类型的文字，然后返回。

## C++ 用法

### 头文件引入

```cpp
#include "DMXMVRFixtureActorInterface.h"
```

### 基本用法

要让你的Actor能被MVR系统识别，需要继承此接口并实现其方法。

**MyActor.h**
```cpp
// 来源: 自定义Actor示例
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXMVRFixtureActorInterface.h" // 引入接口
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor, public IDMXMVRFixtureActorInterface
{
    GENERATED_BODY()

public:
    // 实现接口要求的蓝图可调用函数
    virtual void OnMVRGetSupportedDMXAttributes_Implementation(TArray<FName>& OutAttributeNames, TArray<FName>& OutMatrixAttributeNames) const override;
};
```

**MyActor.cpp**
```cpp
// 来源: 自定义Actor示例
#include "MyActor.h"

void AMyActor::OnMVRGetSupportedDMXAttributes_Implementation(TArray<FName>& OutAttributeNames, TArray<FName>& OutMatrixAttributeNames) const
{
    // 填充此Actor支持的DMX属性
    OutAttributeNames.Add(FName(TEXT("Color")));
    OutAttributeNames.Add(FName(TEXT("Intensity")));

    // 如果没有矩阵属性，留空即可
    // OutMatrixAttributeNames.Add(FName(TEXT("MatrixPixelColor")));
}
```

### 进阶用法

通常，这个接口的实现会与你的 `UDMXComponent` 联动。你可以从 `DMXComponent` 中动态获取当前支持的属性列表，然后通过这个接口提供给外部系统。

```cpp
void AMyActor::OnMVRGetSupportedDMXAttributes_Implementation(TArray<FName>& OutAttributeNames, TArray<FName>& OutMatrixAttributeNames) const
{
    if (UDMXComponent* DMXComp = FindComponentByClass<UDMXComponent>())
    {
        // 假设DMXComponent有一个方法可以获取它当前Fixture Patch所支持的属性列表
        // 实际API需查阅DMX插件文档
        // DMXComp->GetSupportedAttributes(OutAttributeNames);
    }
}
```

## Demo 示例

下面是一个最小化的、可编译的Actor示例，它实现了 `IDMXMVRFixtureActorInterface`。

**MinimalMVRActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXMVRFixtureActorInterface.h"
#include "MinimalMVRActor.generated.h"

UCLASS()
class AMinimalMVRActor : public AActor, public IDMXMVRFixtureActorInterface
{
    GENERATED_BODY()

public:
    AMinimalMVRActor();

    virtual void OnMVRGetSupportedDMXAttributes_Implementation(TArray<FName>& OutAttributeNames, TArray<FName>& OutMatrixAttributeNames) const override;
};
```

**MinimalMVRActor.cpp**
```cpp
#include "MinimalMVRActor.h"

AMinimalMVRActor::AMinimalMVRActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMinimalMVRActor::OnMVRGetSupportedDMXAttributes_Implementation(TArray<FName>& OutAttributeNames, TArray<FName>& OutMatrixAttributeNames) const
{
    // 报告此Minimal Actor支持一个自定义的‘Brightness’属性
    OutAttributeNames.Add(FName(TEXT("Brightness")));
    // 不支持矩阵属性
}
```

## 模块依赖

该插件本身模块 `DMXFixtureActorInterface` 的 `Build.cs` 依赖极为简单，仅包含核心引擎模块，没有额外的特殊依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-17 | `29962d04` | DMX: Remove experimental and beta flags from DMX plugins. All DMX plugins are now production ready | 移除了DMX相关插件的实验性标志，所有DMX插件现已标记为生产就绪 |
| 2024-03-28 | `d827381e` | Fixing case of //Fortnite/Release-29.20/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures/Sour | 修正了部分文件路径的大小写问题 |
| 2024-03-28 | `02c97c27` | Fixing case of //Fortnite/Release-29.20/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures/Sour | 修正了部分文件路径的大小写问题 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接，使用安全协议（HTTPS） |
| 2022-09-26 | `fad85fe0` | DMX - Rework DMXMVRFixtureActorInterface so that it does not require a DMX dependency | 重构DMX模块，使DMXMVRFixtureActorInterface不再依赖DMX模块 |

### 维护评价

- **创建时间**：2022年9月，插件历史约3年。
- **近期更新**：最近一次实质性功能更新是2024年9月，移除了实验性标志，表明插件已达到稳定版本。此后仅有零星的路径大小写修正，无新功能或重大bug修复。
- **活跃程度**：**维护不活跃**。核心功能稳定，自2024年9月后无功能性更新，属于完成其初始设计目标后进入维护状态的插件。
- **已知问题或限制**：从接口设计看，它要求实现Actor必须拥有一个 `DMXComponent` 子对象。这是一个强约束。
- **推荐使用**：**推荐使用**。如果你需要在DMX（MVR）工作流中集成自定义Actor，这是一个官方提供的标准、轻量级且已经生产就绪的接口。代码量极少，依赖清晰，风险低。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/DMX/DMXModularFeaturesTests) (如果存在)