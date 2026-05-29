# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX 引擎 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Runtime), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMX Engine 是 Unreal Engine 虚拟制片管线中用于与 DMX 灯光控制设备通信的核心运行时插件。DMX512 是灯光行业的标准通信协议，广泛用于控制舞台灯光、LED 面板、追光灯等专业灯光设备。

该插件解决的核心问题：
- **DMX 协议收发**：通过 Art-Net 和 sACN 等网络协议向物理灯光设备发送 DMX 数据，并接收来自控制台（如 grandMA）的 DMX 信号
- **Fixture 定义与管理**：通过 DMX Library 资产管理灯光设备（Fixture）的类型定义、通道分配（Patch）和模式（Mode），支持导入 GDTF（General Device Type Format）行业标准文件
- **Sequencer 集成**：允许在 Sequencer 中精确控制灯光设备的每个 DMX 属性，实现基于时间线的灯光动画
- **MVR 支持**：支持 My Virtual Rig（MVR）场景描述格式的导入导出，实现与 Vectorworks 等 3D 设计软件的互操作
- **蓝图友好**：提供完整的蓝图节点用于发送/接收 DMX、查询 Fixture 信息、转换数据格式

## 使用场景

- 你需要在虚拟制片中控制物理灯光设备 → 通过 Output Port 发送 DMX
- 你需要接收灯光控制台（如 grandMA）的 DMX 信号来同步虚拟灯光 → 通过 Input Port 接收 DMX
- 你需要在 Sequencer 中制作精确的灯光动画 → 使用 DMX Library Track
- 你需要与 Vectorworks 互换灯光场景数据 → 使用 MVR 导入/导出功能
- 你需要控制 LED 像素面板的矩阵排列 → 使用 Fixture Matrix + Pixel Mapping Distribution
- 你需要在蓝图中根据接收到的 DMX 值驱动 Actor 行为 → 使用 DMXComponent

## 蓝图用法

### 核心节点

#### DMX 数据收发（UDMXSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Send DMX To Output Port` | 通过指定的 Output Port 发送 DMX 通道值 | `UDMXSubsystem` |
| `Get DMX Data From Input Port` | 从 Input Port 获取最新 DMX 数据 | `UDMXSubsystem` |
| `Get DMX Data From Output Port` | 从 Output Port 获取最新 DMX 数据 | `UDMXSubsystem` |
| `Clear DMX Buffers` | 清除所有 Port 和 Fixture Patch 的缓冲数据 | `UDMXSubsystem` |
| `Load DMX Libraries Synchronous` | 同步加载项目中所有 DMX Library | `UDMXSubsystem` |
| `Get DMX Libraries` | 获取项目中所有 DMX Library 的软引用（不加载） | `UDMXSubsystem` |

#### Fixture 查询（UDMXSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Fixtures Of Type` | 按 Fixture Type 筛选所有 Fixture Patch | `UDMXSubsystem` |
| `Get All Fixtures Of Category` | 按分类筛选 Fixture Patch | `UDMXSubsystem` |
| `Get All Fixtures In Universe` | 获取指定 Universe 中的所有 Fixture Patch | `UDMXSubsystem` |
| `Get All Fixtures In Library` | 获取 DMX Library 中所有 Fixture Patch | `UDMXSubsystem` |
| `Get All Fixtures With Tag` | 按自定义标签筛选 Fixture Patch | `UDMXSubsystem` |
| `Get Fixture By Name` | 按名称查找 Fixture Patch | `UDMXSubsystem` |
| `Get All Fixture Types In Library` | 获取 DMX Library 中所有 Fixture Type | `UDMXSubsystem` |

#### 数据转换（UDMXSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Bytes To Int` | 将连续 DMX 字节转为 32 位整数 | `UDMXSubsystem` |
| `Bytes To Normalized Value` | 将 DMX 字节转为 0.0-1.0 归一化值 | `UDMXSubsystem` |
| `Normalized Value To Bytes` | 将归一化值转为 DMX 字节数组 | `UDMXSubsystem` |
| `Int To Bytes` | 将整数值转为 DMX 字节数组 | `UDMXSubsystem` |
| `Int To Normalized Value` | 将整数值转为归一化值 | `UDMXSubsystem` |
| `Pixel Mapping Distribution Sort` | 按像素映射分布模式排序数组 | `UDMXSubsystem` |

#### Fixture Patch 操作（UDMXEntityFixturePatch）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Fixture Patch In Library` | 在 DMX Library 中创建新的 Fixture Patch | `UDMXEntityFixturePatch` |
| `Send DMX` | 使用属性名和整数值发送 DMX | `UDMXEntityFixturePatch` |
| `Send Default Values` | 发送所有属性的默认值 | `UDMXEntityFixturePatch` |
| `Send Zero Values` | 发送所有属性的零值 | `UDMXEntityFixturePatch` |
| `Get Attribute Value` | 获取指定属性的原始 DMX 值 | `UDMXEntityFixturePatch` |
| `Get Attribute Values` | 获取所有属性的原始 DMX 值 | `UDMXEntityFixturePatch` |
| `Get Normalized Attribute Values` | 获取所有属性的归一化 DMX 值 | `UDMXEntityFixturePatch` |
| `Send Matrix Cell Value` | 向矩阵坐标发送 DMX 值 | `UDMXEntityFixturePatch` |
| `Send Normalized Matrix Cell Value` | 向矩阵坐标发送归一化 DMX 值 | `UDMXEntityFixturePatch` |
| `Get Matrix Cell Values` | 获取矩阵单元的原始值 | `UDMXEntityFixturePatch` |
| `Get All Matrix Cells` | 获取所有矩阵单元 | `UDMXEntityFixturePatch` |

#### DMX Component（UDMXComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `On Fixture Patch Received` | 委托：当 Fixture Patch 接收到 DMX 时触发 | `UDMXComponent` |
| `On DMX Component Tick` | 委托：每 Tick 触发（用于持续接收 DMX） | `UDMXComponent` |
| `Get Fixture Patch` | 获取组件关联的 Fixture Patch | `UDMXComponent` |
| `Set Fixture Patch` | 设置组件关联的 Fixture Patch | `UDMXComponent` |
| `Set Receive DMX From Patch` | 设置是否接收来自 Patch 的 DMX | `UDMXComponent` |

### 使用示例

**发送 DMX 到灯光设备：**
1. 获取 `DMX Subsystem` → 调用 `Send DMX To Output Port`
2. 指定 `Output Port Reference`（在项目设置中配置）
3. 创建一个 `TMap<int32, uint8>`，键为 DMX 通道号（1-512），值为通道值（0-255）
4. 设置 `Local Universe`（默认 1）

**接收 DMX 并驱动 Actor：**
1. 在 Actor 上添加 `DMX Component`
2. 设置 `Fixture Patch Reference` 指向你要监听的 Fixture Patch
3. 勾选 `Receive DMX From Patch`
4. 连接 `On Fixture Patch Received` 委托
5. 在回调中使用 `Value Per Attribute` Map 获取各属性的归一化值（0.0-1.0）

**在 Sequencer 中动画灯光：**
1. 创建 `DMX Library Track`，指定 DMX Library
2. 添加 Fixture Patch 到 Section
3. 为每个通道添加曲线关键帧
4. 支持归一化值模式（0.0-1.0）和绝对值模式（取决于数据类型）

## C++ 用法

### 头文件引入

```cpp
#include "DMXSubsystem.h"
#include "DMXEntityFixturePatch.h"
#include "DMXEntityFixtureType.h"
#include "DMXLibrary.h"
#include "DMXComponent.h"
#include "DMXTypes.h"
```

### 基本用法

**发送 DMX 数据到 Output Port：**

```cpp
#include "DMXSubsystem.h"

// 获取 Subsystem 实例
UDMXSubsystem* DMXSubsystem = UDMXSubsystem::GetDMXSubsystem_Pure();

// 构造通道值映射
TMap<int32, uint8> ChannelToValueMap;
ChannelToValueMap.Add(1, 255);  // 通道 1 = 255
ChannelToValueMap.Add(2, 128);  // 通道 2 = 128
ChannelToValueMap.Add(3, 0);    // 通道 3 = 0

// 发送到指定 Output Port
FDMXOutputPortReference OutputPortRef; // 需要在项目设置中配置
UDMXSubsystem::SendDMXToOutputPort(OutputPortRef, ChannelToValueMap, 1 /*LocalUniverse*/);
```

**接收 DMX 数据：**

```cpp
#include "DMXSubsystem.h"

// 从 Input Port 读取 DMX 数据
FDMXInputPortReference InputPortRef;
TArray<uint8> DMXData;
UDMXSubsystem::GetDMXDataFromInputPort(InputPortRef, DMXData, 1 /*LocalUniverse*/);

if (DMXData.Num() > 0)
{
    // DMXData[0] 是通道 1 的值 (0-255)
    // DMXData[1] 是通道 2 的值 (0-255)
    // ...
}
```

**使用 Fixture Patch 发送和接收 DMX：**

```cpp
#include "DMXEntityFixturePatch.h"

// 创建 Fixture Patch
FDMXEntityFixturePatchConstructionParams Params;
Params.FixtureTypeRef = FixtureTypeRef;
Params.ActiveMode = 0;
Params.UniverseID = 1;
Params.StartingAddress = 1;

UDMXEntityFixturePatch* Patch = UDMXEntityFixturePatch::CreateFixturePatchInLibrary(
    Params, TEXT("My Patch"));

// 发送 DMX（使用属性名）
TMap<FDMXAttributeName, int32> AttributeMap;
FDMXAttributeName DimmerAttr;
DimmerAttr.Name = FName("Dimmer");
AttributeMap.Add(DimmerAttr, 255);
Patch->SendDMX(AttributeMap);

// 获取接收到的属性值
TMap<FDMXAttributeName, int32> ReceivedValues;
Patch->GetAttributeValues(ReceivedValues);

// 获取归一化属性值 (0.0-1.0)
FDMXNormalizedAttributeValueMap NormalizedValues;
Patch->GetNormalizedAttributeValues(NormalizedValues);

// 监听 DMX 接收事件（Native 委托）
Patch->OnFixturePatchReceivedDMXNative.AddLambda(
    [](UDMXEntityFixturePatch* InPatch, const FDMXNormalizedAttributeValueMap& Values)
    {
        // 处理接收到的 DMX 数据
        const float* DimmerValue = Values.Map.Find(FDMXAttributeName(FName("Dimmer")));
        if (DimmerValue)
        {
            // DimmerValue 在 0.0 - 1.0 范围
        }
    });
```

### 进阶用法

**矩阵 Fixture（Matrix Fixture）操作：**

```cpp
#include "DMXEntityFixturePatch.h"

// 获取矩阵属性
FDMXFixtureMatrix MatrixProperties;
if (Patch->GetMatrixProperties(MatrixProperties))
{
    // 这是一个矩阵 Fixture
    int32 XCells = MatrixProperties.XCells;  // 列数
    int32 YCells = MatrixProperties.YCells;  // 行数
    
    // 向特定单元格发送颜色值
    FIntPoint CellCoord(0, 0); // 左上角
    FDMXAttributeName RedAttr;
    RedAttr.Name = FName("ColorAddRed");
    Patch->SendMatrixCellValue(CellCoord, RedAttr, 255);
    
    // 使用归一化值发送
    Patch->SendNormalizedMatrixCellValue(CellCoord, RedAttr, 1.0f);
    
    // 获取单元格的通道分配
    TMap<FDMXAttributeName, int32> ChannelMap;
    Patch->GetMatrixCellChannelsAbsolute(CellCoord, ChannelMap);
}
```

**数据格式转换：**

```cpp
#include "DMXSubsystem.h"

UDMXSubsystem* Subsystem = GetWorld()->GetSubsystem<UDMXSubsystem>();

// 字节数组 → 整数值（支持 MSB/LSB）
TArray<uint8> Bytes = {0, 0, 1}; // 16bit: 256 (MSB模式)
int32 IntValue = Subsystem->BytesToInt(Bytes, false /*bUseLSB*/);

// 字节数组 → 归一化值
float Normalized = Subsystem->BytesToNormalizedValue(Bytes, false);

// 归一化值 → 字节数组（根据信号格式自动确定精度）
TArray<uint8> OutBytes;
Subsystem->NormalizedValueToBytes(0.5f, EDMXFixtureSignalFormat::E16Bit, OutBytes, false);

// 整数 → 字节数组
TArray<uint8> IntBytes;
UDMXSubsystem::IntValueToBytes(1000, EDMXFixtureSignalFormat::E16Bit, IntBytes, false);
```

**DMX Library 与 Fixture Type 查询：**

```cpp
#include "DMXLibrary.h"
#include "DMXEntityFixtureType.h"

// 获取所有 DMX Library
TArray<TSoftObjectPtr<UDMXLibrary>> Libraries = Subsystem->GetDMXLibraries();

// 加载并查询
TArray<UDMXLibrary*> LoadedLibraries = Subsystem->LoadDMXLibrariesSynchronous();

for (UDMXLibrary* Library : LoadedLibraries)
{
    // 获取所有 Fixture Type
    TArray<UDMXEntityFixtureType*> FixtureTypes = Subsystem->GetAllFixtureTypesInLibrary(Library);
    
    // 获取特定 Fixture Type 的所有 Patch
    for (UDMXEntityFixtureType* FixtureType : FixtureTypes)
    {
        FDMXEntityFixtureTypeRef TypeRef(FixtureType);
        TArray<UDMXEntityFixturePatch*> Patches;
        Subsystem->GetAllFixturesOfType(TypeRef, Patches);
    }
    
    // 按标签查询
    TArray<UDMXEntityFixturePatch*> TaggedPatches = 
        Subsystem->GetAllFixturesWithTag(Library, FName("MainLight"));
}
```

## Demo 示例

**最小 DMX 接收器 Actor：**

```cpp
// DMXReceiverActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXEntityFixturePatch.h"
#include "DMXReceiverActor.generated.h"

UCLASS()
class ADMXReceiverActor : public AActor
{
    GENERATED_BODY()

public:
    ADMXReceiverActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** Fixture Patch to listen to */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DMX")
    FDMXEntityFixturePatchRef FixturePatchRef;

private:
    /** Callback when DMX is received */
    void OnDMXReceived(UDMXEntityFixturePatch* FixturePatch, 
                       const FDMXNormalizedAttributeValueMap& NormalizedValues);

    /** Handle to the bound delegate */
    FDelegateHandle DelegateHandle;
};
```

```cpp
// DMXReceiverActor.cpp
#include "DMXReceiverActor.h"
#include "DMXEntityFixturePatch.h"

ADMXReceiverActor::ADMXReceiverActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADMXReceiverActor::BeginPlay()
{
    Super::BeginPlay();

    UDMXEntityFixturePatch* Patch = FixturePatchRef.GetFixturePatch();
    if (Patch)
    {
        // 绑定 DMX 接收事件
        DelegateHandle = Patch->OnFixturePatchReceivedDMXNative.AddUObject(
            this, &ADMXReceiverActor::OnDMXReceived);
    }
}

void ADMXReceiverActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UDMXEntityFixturePatch* Patch = FixturePatchRef.GetFixturePatch();
    if (Patch && DelegateHandle.IsValid())
    {
        Patch->OnFixturePatchReceivedDMXNative.Remove(DelegateHandle);
    }

    Super::EndPlay(EndPlayReason);
}

void ADMXReceiverActor::OnDMXReceived(UDMXEntityFixturePatch* FixturePatch, 
                                       const FDMXNormalizedAttributeValueMap& NormalizedValues)
{
    // 读取 Dimmer 归一化值 (0.0 - 1.0)
    const FDMXAttributeName DimmerAttr(FName("Dimmer"));
    const float* DimmerValue = NormalizedValues.Map.Find(DimmerAttr);
    if (DimmerValue)
    {
        UE_LOG(LogTemp, Log, TEXT("Dimmer: %.2f"), *DimmerValue);
    }

    // 读取 RGB 颜色
    const FDMXAttributeName RedAttr(FName("ColorAddRed"));
    const FDMXAttributeName GreenAttr(FName("ColorAddGreen"));
    const FDMXAttributeName BlueAttr(FName("ColorAddBlue"));

    const float* R = NormalizedValues.Map.Find(RedAttr);
    const float* G = NormalizedValues.Map.Find(GreenAttr);
    const float* B = NormalizedValues.Map.Find(BlueAttr);

    if (R && G && B)
    {
        FLinearColor Color(*R, *G, *B);
        UE_LOG(LogTemp, Log, TEXT("Color: R=%.2f G=%.2f B=%.2f"), *R, *G, *B);
    }
}
```

## 模块依赖

DMXEngine 的模块依赖主要来自 DMXProtocol 插件和 UE 核心模块。由于提供的信息中未包含完整的 Build.cs 内容，根据代码分析的依赖如下：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | DMX 协议层（Art-Net/sACN 通信实现） |
| `DMXGDTF` | GDTF 文件解析（General Device Type Format） |
| `DMXFixtureActorInterface` | MVR Fixture Actor 接口定义 |
| `MovieScene` | Sequencer 影片场景集成 |
| `Json` | JSON 序列化（用于可选类型和运行时工具） |
| `XmlParser` | MVR XML 解析 |
| `AssetRegistry` | DMX Library 资产发现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `96d3b290` | DMX - Fix a crash when trying to edit a sequence with a fixture patch that no longer contains a mode | 修复 Sequencer 编辑中 Fixture Patch 无有效模式时的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制片资产分类和迁移 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | IsSavingPackage 相关改动 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 清理废弃的 include 和头文件 |

### 维护评价

- **活跃维护**：该插件持续获得功能性更新和 Bug 修复，最近一次更新距今仅数周
- **成熟度高**：代码中有大量已废弃（Deprecated）的 API，说明经历了多次重大重构（4.26→4.27 Controllers 移除为 Ports、5.0 实体管理重构、5.5 GDTF 架构升级），API 设计趋于稳定
- **已知限制**：
  - DMX 数据的 Tick 级精度受引擎 Tick 频率限制，高精度灯光控制可能需要额外优化
  - 许多旧版 API 已标记为 Deprecated（4.27 Controllers、5.0 实体管理、5.5 GDTF 导入），新项目应使用最新的 Port + FixturePatch API
  - MVR 支持在持续完善中，部分 GDTF 导入类型已迁移到独立的 DMXGDTF 模块
- **推荐使用**：✅ 推荐。作为 Epic 官方维护的虚拟制片核心组件，该插件是 UE5 DMX 灯光控制的唯一标准方案，维护活跃且功能完善

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [DMXEngine Plugin - Unreal Engine 官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/dmx-engine-plugin-for-unreal-engine)
- [DMX Fixture Patch - Unreal Engine 官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/dmx-fixture-patch-in-unreal-engine)