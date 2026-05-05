# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Editor), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-02-19 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMX Engine 是 Unreal Engine 虚拟制片管线中用于与 DMX（Digital Multiplex）协议设备通信的核心插件。DMX512 是舞台灯光、特效设备和演出控制领域的行业标准协议，广泛用于演唱会、剧院、建筑照明等场景。

该插件解决的核心问题是：**在 Unreal Engine 中建立与真实世界 DMX 灯光/特效设备的双向通信**。它提供了：

- **DMXRuntime**：运行时核心，负责 DMX 协议通信、Fixture Type/Patch 等实体的数据模型管理、DMX 数据的发送与接收
- **DMXEditor**：编辑器工具，提供 DMX Library 编辑器、Fixture Type/Patch 配置界面、DMX 监控面板等
- **DMXBlueprintGraph**：自定义蓝图节点，让设计师无需编写 C++ 即可在蓝图中读取 DMX 属性值、引用 Fixture Patch/Type

典型工作流：在 DMX Library 中定义灯具类型（Fixture Type）和灯具实例（Fixture Patch），然后通过蓝图或 C++ 读取/发送 DMX 通道数据，实现虚拟灯光与真实灯光的同步控制。

## 使用场景

- 你在做虚拟制片，需要让 Unreal Engine 中的灯光与片场真实 DMX 灯具同步 → 用 DMXEngine 配置 Fixture Patch 并通过蓝图驱动灯光
- 你在做演唱会/舞台演出的实时预可视化（Previs） → 用 DMXEngine 接收灯光控制台的 DMX 数据，实时驱动引擎中的灯光效果
- 你需要在蓝图中根据 DMX Fixture Type 动态获取灯具属性（如颜色、亮度、频闪） → 用 `GetDMXAttributeValues` 蓝图节点
- 你在构建建筑照明可视化系统，需要从 DMX 控制器读取数据 → 用 DMXRuntime 的运行时通信功能

## 蓝图用法

DMXBlueprintGraph 模块提供了多个自定义 K2 节点，用于在蓝图中引用 DMX 实体和获取属性值。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Get DMX Fixture Type | 获取 DMX Fixture Type 引用（纯函数节点） | `UK2Node_GetDMXFixtureType` |
| Get DMX Fixture Patch | 获取 DMX Fixture Patch 引用（纯函数节点） | `UK2Node_GetDMXFixturePatch` |
| Get DMX Attribute Values | 从 Fixture Patch 中提取各属性值，输出为独立引脚 | `UK2Node_GetDMXAttributeValues` |

### Get DMX Fixture Patch 节点

该节点是蓝图中引用 DMX Fixture Patch 的主要方式。它是一个纯函数节点（`IsNodePure() = true`），输出一个 `FDMXEntityFixturePatchRef` 引用。

**使用方式**：
1. 在蓝图中右键搜索 "Get DMX Fixture Patch"
2. 节点提供一个输入引脚（Fixture Patch 引用选择器）和一个输出引脚（Fixture Patch 引用）
3. 通过下拉菜单选择目标 Fixture Patch
4. 输出引脚可连接到其他 DMX 节点

### Get DMX Attribute Values 节点

这是最常用的 DMX 蓝图节点，用于从 Fixture Patch 中提取灯具属性值（如颜色、亮度、频闪等）。

**使用方式**：
1. 在蓝图中添加 "Get DMX Attribute Values" 节点
2. 连接一个 Fixture Patch 引用到输入引脚
3. 节点会根据 Fixture Patch 关联的 Fixture Type 的当前模式（Mode），自动暴露对应的属性引脚
4. 输出引脚包括：
   - **Attributes Map**：属性名到值的映射
   - **Is Success**：是否成功获取属性值
   - 各个 DMX Function 对应的独立输出引脚（如 Color、Intensity 等）

**动态引脚更新**：当输入的 Fixture Patch 变更或关联的 Fixture Type 更新时，节点会自动重新生成输出引脚以匹配当前模式的属性定义。

### 使用示例（蓝图描述）

**场景：读取 DMX 灯具颜色并应用到场景光源**

1. 创建一个 Actor 蓝图，添加一个 Point Light 组件
2. 在 Event Tick 中：
   - 添加 "Get DMX Fixture Patch" 节点，选择目标灯具
   - 将输出连接到 "Get DMX Attribute Values" 节点的输入
   - 从 "Get DMX Attribute Values" 的 Color 输出引脚获取颜色值
   - 通过 "Set Light Color" 节点将颜色应用到 Point Light

**场景：根据 DMX 数据控制物体位置**

1. 添加 "Get DMX Fixture Patch" 和 "Get DMX Attribute Values" 节点
2. 从 Pan/Tilt 属性引脚获取值
3. 通过数学节点将 DMX 值（0-255 或 0-65535）映射到旋转角度
4. 应用到目标 Actor 的旋转

## C++ 用法

### 头文件引入

```cpp
// DMX 实体引用和数据类型
#include "Library/DMXEntityReference.h"

// Fixture Type 和 Patch 实体
#include "DMXEntityFixtureType.h"
#include "DMXEntityFixturePatch.h"

// 自定义蓝图节点（仅在扩展蓝图图时需要）
#include "K2Node_GetDMXFixturePatch.h"
#include "K2Node_GetDMXFixtureType.h"
#include "K2Node_GetDMXAttributeValues.h"
```

### 基本用法：通过 Fixture Patch 引用获取属性值

```cpp
// 来源: K2Node_GetDMXAttributeValues.h - GetFixturePatchFromPin / GetActiveFixtureMode

// 获取 Fixture Patch 对象
UDMXEntityFixturePatch* FixturePatch = /* 从 DMX Library 中获取 */;

if (FixturePatch)
{
    // 获取当前激活的模式
    const FDMXFixtureMode* ActiveMode = FixturePatch->GetActiveMode();
    
    if (ActiveMode)
    {
        // 遍历模式中的所有 Function（属性）
        for (const FDMXFixtureFunction& Function : ActiveMode->Functions)
        {
            // 获取属性名称
            FName AttributeName = Function.AttributeName;
            
            // 获取属性值（根据通道数可能是 8bit 或 16bit）
            int32 ChannelValue = FixturePatch->GetAttributeValue(AttributeName);
            
            UE_LOG(LogTemp, Log, TEXT("Attribute: %s, Value: %d"), *AttributeName.ToString(), ChannelValue);
        }
    }
}
```

### 进阶用法：程序化创建 Fixture Patch 引用

```cpp
// 来源: K2Node_GetDMXFixturePatch.h - FDMXEntityFixtureTypeRef / FDMXEntityFixturePatchRef

// 创建 Fixture Type 引用
FDMXEntityFixtureTypeRef FixtureTypeRef;
FixtureTypeRef.SetEntity(FixtureTypeObject);

// 创建 Fixture Patch 引用
FDMXEntityFixturePatchRef FixturePatchRef;
FixturePatchRef.SetEntity(FixturePatchObject);

// 从引用中获取实际对象
UDMXEntityFixtureType* ResolvedType = FixtureTypeRef.GetFixtureType();
UDMXEntityFixturePatch* ResolvedPatch = FixturePatchRef.GetFixturePatch();

if (ResolvedPatch && ResolvedType)
{
    // 验证 Patch 是否属于该 Type
    if (ResolvedPatch->GetParentFixtureType() == ResolvedType)
    {
        // 安全地获取属性值
        const FDMXFixtureMode* Mode = ResolvedPatch->GetActiveMode();
        for (const FDMXFixtureFunction& Func : Mode->Functions)
        {
            int32 Value = ResolvedPatch->GetAttributeValue(Func.AttributeName);
            // 处理 DMX 值...
        }
    }
}
```

## Demo 示例

以下示例展示如何创建一个自定义蓝图节点，从 DMX Fixture Patch 读取颜色属性并返回 FLinearColor：

```cpp
// DMXColorReaderNode.h
#pragma once

#include "CoreMinimal.h"
#include "K2Node.h"
#include "Library/DMXEntityReference.h"
#include "DMXColorReaderNode.generated.h"

UCLASS()
class UDMXColorReaderNode : public UK2Node
{
    GENERATED_BODY()

public:
    virtual void AllocateDefaultPins() override;
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual FText GetTooltipText() const override;
    virtual bool IsNodePure() const override { return true; }
    virtual void ExpandNode(class FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph) override;
    virtual FText GetMenuCategory() const override;

    static const FName InputPatchPinName;
    static const FName OutputColorPinName;
    static const FName OutputSuccessPinName;
};
```

```cpp
// DMXColorReaderNode.cpp
#include "DMXColorReaderNode.h"
#include "DMXEntityFixturePatch.h"
#include "KismetCompiler.h"
#include "BlueprintActionDatabaseRegistrar.h"
#include "K2Node_CallFunction.h"

const FName UDMXColorReaderNode::InputPatchPinName(TEXT("FixturePatch"));
const FName UDMXColorReaderNode::OutputColorPinName(TEXT("Color"));
const FName UDMXColorReaderNode::OutputSuccessPinName(TEXT("bSuccess"));

void UDMXColorReaderNode::AllocateDefaultPins()
{
    // 输入：Fixture Patch 引用
    CreatePin(EGPD_Input, UEdGraphPin::PC_Struct, 
        FDMXEntityFixturePatchRef::StaticStruct(), InputPatchPinName);
    
    // 输出：颜色值和成功标志
    CreatePin(EGPD_Output, UEdGraphPin::PC_Struct, 
        TBaseStructure<FLinearColor>::Get(), OutputColorPinName);
    CreatePin(EGPD_Output, UEdGraphPin::PC_Boolean, 
        TEXT("bSuccess"), OutputSuccessPinName);
}

FText UDMXColorReaderNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return FText::FromString(TEXT("Get DMX Color"));
}

FText UDMXColorReaderNode::GetTooltipText() const
{
    return FText::FromString(TEXT("Reads color attributes from a DMX Fixture Patch and returns a LinearColor"));
}

void UDMXColorReaderNode::ExpandNode(FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph)
{
    Super::ExpandNode(CompilerContext, SourceGraph);
    // 展开为实际的函数调用节点...
}

FText UDMXColorReaderNode::GetMenuCategory() const
{
    return FText::FromString(TEXT("DMX"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXRuntime` | DMX 核心运行时，提供 Fixture Type/Patch 实体类、DMX 协议通信 |
| `KismetCompiler` | 蓝图编译器，用于 K2Node 的 ExpandNode 展开 |
| `BlueprintGraph` | 蓝图图编辑基础框架，K2Node 基类 |

## 维护状态

### 近期更新

```
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
- bd46f624150a DMX: Clean up DMX Engine blueprint nodes, improve comments, clean up API
- 64ae24ec12e2 Removed extraneous GetSelfPin implementations
```

### 维护评价

DMX Engine 插件创建于 2020 年，是 Unreal Engine 虚拟制片管线的重要组成部分。从近期提交记录来看，维护活动集中在代码清理和 API 规范化（移除 FORCEINLINE、清理蓝图节点、改进注释），属于稳定的维护性更新而非新功能开发。

**优点**：
- 作为 Epic 官方维护的虚拟制片核心组件，有持续的维护保障
- 代码质量在持续改善（清理冗余实现、规范化 API）
- 提供了完整的蓝图节点支持，降低使用门槛

**注意事项**：
- `UDEPRECATED_K2Node_CastPatchToType` 已标记为废弃，新项目应使用 `UK2Node_GetDMXAttributeValues` 替代
- DMXBlueprintGraph 模块类型为 UncookedOnly，仅在编辑器和开发构建中可用
- 该插件默认未启用，需要在项目设置中手动启用

**推荐使用**：✅ 推荐。对于任何涉及 DMX 设备控制的虚拟制片项目，这是标准且必要的插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [DMXBlueprintGraph 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXBlueprintGraph)
- [DMXRuntime 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXRuntime)
- [DMXEditor 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXEditor)