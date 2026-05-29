# LocationServicesBPLibrary

> Common interface for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | 移动位置服务库 |
| 分类 | Mobile |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesBPLibrary` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesBPLibrary) | |

## 用途

该插件提供了一个**跨移动平台（iOS和Android）的、统一的位置服务蓝图接口**。它封装了原生平台的GPS定位API，使得在UE4项目中，开发者无需关心iOS（Core Location）和Android（LocationManager）之间的API差异，就能通过蓝图节点获取设备的实时经纬度、海拔、精度等地理位置信息。其核心价值在于简化了移动端定位功能的跨平台开发流程。

## 使用场景

- 你正在开发一款基于地理位置的AR游戏（如Pokémon GO），需要持续获取玩家的实时坐标。
- 你的应用需要记录用户的行进轨迹、计算移动距离或速度。
- 你需要根据设备位置动态加载周边的地点信息或触发特定的游戏事件。

## 蓝图用法

插件的核心功能通过静态函数暴露在蓝图中，主要集中在 `ULocationServices` 类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init Location Services` | 使用指定的精度、更新频率和最小移动距离初始化位置服务。**必须先调用此节点**。 | `ULocationServices` |
| `Start Location Services` | 开始接收位置更新。必须在初始化成功后调用。 | `ULocationServices` |
| `Stop Location Services` | 停止接收位置更新。 | `ULocationServices` |
| `Get Last Known Location` | 获取最后一次成功获取到的位置数据（`FLocationServicesData` 结构体）。 | `ULocationServices` |
| `Are Location Services Enabled` | 检查设备是否为此应用启用了位置服务（例如用户是否授予了权限）。 | `ULocationServices` |
| `Is Location Accuracy Available` | 检查当前设备是否支持指定的精度等级。 | `ULocationServices` |
| `Get Location Services Impl` | 获取底层平台实现对象，可用于访问 `OnLocationChanged` 事件。 | `ULocationServices` |

### 使用示例（蓝图描述）

一个典型的定位流程蓝图如下：
1.  调用 `Are Location Services Enabled` 节点检查权限。
2.  如果已启用，调用 `Init Location Services` 节点，设置 `Accuracy` 为 `Best`，`UpdateFrequency` 为 `1000`（毫秒），`MinDistanceFilter` 为 `0`。
3.  调用 `Start Location Services` 节点启动服务。
4.  将 `Get Location Services Impl` 节点的返回值拖出，获取其 `OnLocationChanged` 委托，将其绑定到一个自定义事件（例如 `OnLocationUpdated`）。
5.  在 `OnLocationUpdated` 事件中，可以从参数中获取 `FLocationServicesData`，并读取其中的 `Longitude`、`Latitude` 等属性。
6.  在需要停止时（如界面关闭），调用 `Stop Location Services` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "LocationServicesBPLibrary.h"
#include "LocationServicesImpl.h" // 如果需要访问事件委托
```

### 基本用法

基本用法与蓝图类似，通过静态函数控制。

```cpp
// （示例代码，基于源码逻辑编写）
// 初始化位置服务
bool bInitSuccess = ULocationServices::InitLocationServices(
    ELocationAccuracy::LA_Best,
    1000.0f, // 更新频率，单位毫秒
    0.0f     // 最小移动距离，单位米
);

if (bInitSuccess)
{
    // 启动服务
    bool bStartSuccess = ULocationServices::StartLocationServices();
    
    // ... 在合适的时候停止
    // ULocationServices::StopLocationServices();
}

// 获取最后已知位置
FLocationServicesData LastLocation = ULocationServices::GetLastKnownLocation();
UE_LOG(LogTemp, Log, TEXT("Last Location: Lat=%f, Lon=%f"), LastLocation.Latitude, LastLocation.Longitude);
```

### 进阶用法

可以通过平台实现对象绑定位置更新事件。

```cpp
// 获取平台实现对象
ULocationServicesImpl* LocationImpl = ULocationServices::GetLocationServicesImpl();
if (LocationImpl)
{
    // 绑定位置变化事件
    LocationImpl->OnLocationChanged.AddDynamic(this, &UMyLocationComponent::HandleLocationChanged);
}

// 事件处理函数
void UMyLocationComponent::HandleLocationChanged(const FLocationServicesData& LocationData)
{
    // 处理新的位置数据
    FVector NewLocation(LocationData.Longitude, LocationData.Latitude, LocationData.Altitude);
    // ... 更新游戏内对象位置等逻辑
}
```

## Demo 示例

一个最小的可编译示例，用于获取并打印单次位置信息。

**MyLocationComponent.h**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LocationServicesBPLibrary.h" // 插件核心头文件
#include "MyLocationComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyLocationComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UMyLocationComponent();

protected:
	virtual void BeginPlay() override;

public:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	UFUNCTION(BlueprintCallable, Category = "Location")
	void RequestOneShotLocation();

	UFUNCTION()
	void OnLocationUpdated(const FLocationServicesData& LocationData);

	bool bLocationRequested = false;
};
```

**MyLocationComponent.cpp**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。
#include "MyLocationComponent.h"
#include "LocationServicesImpl.h" // 用于访问事件委托

UMyLocationComponent::UMyLocationComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UMyLocationComponent::BeginPlay()
{
	Super::BeginPlay();
	// 立即请求一次位置
	RequestOneShotLocation();
}

void UMyLocationComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
}

void UMyLocationComponent::RequestOneShotLocation()
{
	// 1. 初始化
	bool bInitOk = ULocationServices::InitLocationServices(
		ELocationAccuracy::LA_Best,
		0.0f, // UpdateFrequency 0 可能表示基于距离的更新
		0.0f  // MinDistanceFilter 0 表示任何移动都触发
	);

	if (bInitOk)
	{
		// 2. 获取实现并绑定事件
		ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
		if (Impl)
		{
			Impl->OnLocationChanged.AddDynamic(this, &UMyLocationComponent::OnLocationUpdated);
		}

		// 3. 启动服务
		ULocationServices::StartLocationServices();
		bLocationRequested = true;
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Location Services Init Failed"));
	}
}

void UMyLocationComponent::OnLocationUpdated(const FLocationServicesData& LocationData)
{
	if (bLocationRequested)
	{
		// 成功获取到位置，打印并停止服务
		UE_LOG(LogTemp, Log, TEXT("Location Received - Lat: %f, Lon: %f, Accuracy: %f meters"),
			LocationData.Latitude, LocationData.Longitude, LocationData.HorizontalAccuracy);

		ULocationServices::StopLocationServices();
		bLocationRequested = false;

		// 可选：解绑事件
		ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
		if (Impl)
		{
			Impl->OnLocationChanged.RemoveDynamic(this, &UMyLocationComponent::OnLocationUpdated);
		}
	}
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 优化编译，为自动生成的代码添加内联宏。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 构建系统适配，调整符号导出属性。 |
| 2023-04-12 | `bd466cf2` | Updated modules to not dependency on itself. | 修复构建依赖，移除对自身的循环依赖。 |
| 2022-12-20 | `e8c72824` | [Lyra] | 与Lyra示例项目相关的变更（具体细节未明）。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内置的链接更新为HTTPS协议。 |

### 维护评价

- **创建时间**：插件创建于2016年，历史悠久。
- **近期更新**：最近的实质性更新停留在2023年4月（修复构建依赖）。2025年的更新均为编译和构建系统的全局性优化，并非针对该插件的功能增强或缺陷修复。
- **活跃度**：**维护不活跃**。该插件被视为“功能完成”，近年来只接受必要的编译兼容性维护，没有新功能开发。
- **限制**：作为早期插件，其API相对简单，可能缺少现代位置服务所需的精度控制、后台定位、权限请求流程集成等高级功能。
- **推荐**：如果项目需要快速实现基础的移动端定位功能，且对精度和后台服务要求不高，可以使用。但对于复杂或要求高的定位需求，可能需要考虑更现代的替代方案或自行封装原生API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesBPLibrary)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesBPLibrary)（源码目录内未发现独立测试文件）