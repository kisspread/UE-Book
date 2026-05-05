# SourceFilteringCore 模块

> 最小接口层，定义数据源过滤的核心接口和数据结构。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| LoadingPhase | Default |
| TargetConfigurationDenyList | Shipping |

## 职责

SourceFilteringCore 是插件的最底层模块，只定义接口和基础数据结构，不包含任何实现逻辑。它的设计目标是让其他模块（Runtime 和 Editor）可以在不引入引擎依赖的情况下引用过滤器接口。

## 源文件

| 文件 | 路径 |
|---|---|
| `IDataSourceFilterInterface.h` | [Public](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringCore/Public/IDataSourceFilterInterface.h) |
| `IDataSourceFilterSetInterface.h` | [Public](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringCore/Public/IDataSourceFilterSetInterface.h) |
| `DataSourceFiltering.h` | [Public](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringCore/Public/DataSourceFiltering.h) |
| `TraceSourceFilteringSettings.h` | [Public](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringCore/Public/TraceSourceFilteringSettings.h) |
| `SourceFilteringCore.Build.cs` | [Build](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringCore/SourceFilteringCore.Build.cs) |

## 核心接口

### IDataSourceFilterInterface

所有数据源过滤器的顶层接口，通过 `UINTERFACE(Blueprintable)` 暴露给蓝图系统。

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UDataSourceFilterInterface : public UInterface { ... };

class IDataSourceFilterInterface
{
public:
    // 获取过滤器显示名称（BlueprintNativeEvent，可蓝图重写）
    UFUNCTION(BlueprintNativeEvent)
    void GetDisplayText(FText& OutDisplayText) const;

    // 获取过滤器工具提示（BlueprintNativeEvent，可蓝图重写）
    UFUNCTION(BlueprintNativeEvent)
    void GetToolTipText(FText& OutDisplayText) const;

    // 获取过滤器配置
    virtual const FDataSourceFilterConfiguration& GetConfiguration() const = 0;

    // 启用/禁用过滤器
    virtual void SetEnabled(bool bState) = 0;
    virtual bool IsEnabled() const = 0;
};
```

### FDataSourceFilterConfiguration

过滤器配置结构体，定义了运行时行为参数：

| 字段 | 类型 | 说明 |
|---|---|---|
| `bOnlyApplyDuringActorSpawn` | `bool` | 是否仅在 Actor 生成时应用一次（后续不再评估） |
| `bCanRunAsynchronously` | `bool` | 是否可以在非游戏线程上运行 |
| `FilterApplyingTickInterval` | `uint8` | 过滤器评估间隔帧数（1-255），中间帧使用缓存结果 |

### IDataSourceFilterSetInterface

过滤器集合接口：

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UDataSourceFilterSetInterface : public UInterface { ... };

class IDataSourceFilterSetInterface
{
public:
    virtual EFilterSetMode GetFilterSetMode() const = 0;
};
```

## 核心数据结构

### EFilterSetMode

过滤器集合的逻辑操作模式：

| 值 | 说明 |
|---|---|
| `AND` | 集合内所有过滤器都通过才算通过 |
| `OR` | 集合内任一过滤器通过即算通过 |
| `NOT` | 取反：集合内过滤器不通过才算通过 |

### ESourceActorFilterOperation

Actor 过滤器操作类型，用于 Trace 输出：

| 值 | 说明 |
|---|---|
| `RemoveFilter` | 移除过滤器 |
| `MoveFilter` | 移动过滤器 |
| `ReplaceFilter` | 替换过滤器 |
| `SetFilterMode` | 设置过滤器模式 |
| `SetFilterState` | 设置过滤器启用状态 |

### EWorldFilterOperation

World 过滤器操作类型：

| 值 | 说明 |
|---|---|
| `TypeFilter` | 按 World 类型过滤 |
| `NetModeFilter` | 按网络模式过滤 |
| `InstanceFilter` | 按 World 实例过滤 |
| `RemoveWorld` | 移除 World |

### FActorClassFilter

高级 Actor 类过滤结构体，用于快速过滤特定类的 Actor：

```cpp
USTRUCT()
struct FActorClassFilter
{
    // 目标 Actor 类
    UPROPERTY(EditAnywhere)
    FSoftClassPath ActorClass;

    // 是否包含派生类
    UPROPERTY(EditAnywhere)
    bool bIncludeDerivedClasses = false;
};
```

## UTraceSourceFilteringSettings

全局过滤设置对象，配置文件保存在 `TraceSourceFilters.ini`：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bDrawFilteringStates` | `bool` | 是否用线框盒绘制所有 Actor 的过滤状态 |
| `bDrawOnlyPassingActors` | `bool` | 是否只绘制通过过滤的 Actor |
| `bDrawFilterDescriptionForRejectedActors` | `bool` | 是否在被过滤的 Actor 上绘制失败原因 |
| `bOutputOptimizedFilterState` | `bool` | 是否在过滤设置变更时输出优化后的状态到日志 |

设置变更会广播 `OnSourceFilteringSettingsChanged` 委托。

## 模块依赖

仅依赖 `Core` 和 `CoreUObject`，保持最小依赖。
