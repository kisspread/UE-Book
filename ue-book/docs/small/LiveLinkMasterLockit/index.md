# LiveLinkMasterLockit

> Live Link support for the Ambient MasterLockit metadata server

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | LiveLinkMasterLockit (Runtime), LiveLinkMasterLockitEditor (Editor) |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit) | |

## 用途

LiveLinkMasterLockit 通过 TCP 连接到 **Ambient MasterLockit** 元数据服务器，实时接收摄影机镜头的元数据（焦距、光圈、焦点距离、水平视场角），并将其作为 **LiveLink Camera** 数据推送到 UE5 中。

Ambient MasterLockit 是一套片场（set）元数据管理系统，用于收集和分发来自各种片场设备（摄影机、镜头、录音机、时间码发生器等）的数据。本 plugin 当前仅实现了对 **Carl Zeiss AG** 镜头数据的解析，其他设备类型的 VolatileDataEvent 处理均为 `Unimplemented` 状态。

该 plugin 存在的意义是让 UE5 的 Virtual Production 工作流能够实时获取真实摄影机镜头参数，从而同步 CG 摄影机与物理摄影机的状态——这是 LED Volume 拍摄和虚拟制片的核心需求。

## 使用场景

- 你在使用 **LED Volume** 进行虚拟制片，需要将现场摄影机的镜头参数（焦距、光圈、焦点距离）实时同步到 UE5 中的 CG 摄影机
- 你的片场使用 **Ambient MasterLockit** 系统管理元数据，且使用 **Zeiss** 镜头
- 你需要在 nDisplay 环境中实现镜头数据的实时驱动

## 蓝图用法

本 plugin 没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有功能通过 **LiveLink** 框架的标准 UI 操作：

### 添加 MasterLockit 数据源

1. 打开 **LiveLink** 面板（Window → Live Link）
2. 点击 **Source** 下拉菜单
3. 选择 **MasterLockit**
4. 在弹出的面板中填写：
   - **IPAddress**: MasterLockit 服务器的 IP 地址（默认 `0.0.0.0`）
   - **SubjectName**: LiveLink Subject 名称（默认 `MasterLockitDevice`）
5. 点击 **Ok** 连接

### 使用 LiveLink 数据

连接成功后，MasterLockit 会创建一个 **Camera** 类型的 LiveLink Subject，提供以下属性：

| 属性 | 说明 |
|---|---|
| FocalLength | 焦距 (mm) |
| Aperture | 光圈 (T 值) |
| FocusDistance | 焦点距离 |
| FieldOfView | 水平视场角 |
| SceneTime | 帧时间码 |

在蓝图中通过 **LiveLink Transform Controller** 或 **Get LiveLink Data** 节点即可获取这些数据并驱动 CG 摄影机。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkMasterLockitConnectionSettings.h"
#include "LiveLinkMasterLockitFactory.h"
```

### 基本用法

通过 `ULiveLinkMasterLockitSourceFactory::CreateConnectionString` 序列化连接设置，然后用 `CreateSource` 创建数据源：

```cpp
// 来源: Source/LiveLinkMasterLockit/Private/LiveLinkMasterLockitFactory.cpp
FLiveLinkMasterLockitConnectionSettings Settings;
Settings.IPAddress = TEXT("192.168.1.100");
Settings.SubjectName = TEXT("MyCamera");

// 序列化为连接字符串
FString ConnectionString = ULiveLinkMasterLockitSourceFactory::CreateConnectionString(Settings);

// 创建 LiveLink 源
TSharedPtr<ILiveLinkSource> Source = Factory->CreateSource(ConnectionString);
```

### 连接设置结构

```cpp
// 来源: Source/LiveLinkMasterLockit/Public/LiveLinkMasterLockitConnectionSettings.h
USTRUCT()
struct FLiveLinkMasterLockitConnectionSettings
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Settings")
    FString IPAddress = TEXT("0.0.0.0");

    UPROPERTY(EditAnywhere, Category = "Settings")
    FName SubjectName = TEXT("MasterLockitDevice");
};
```

## Demo 示例

本 plugin 是纯 Runtime + Editor 模块，无独立 demo 项目。使用方式：

1. 在 `Plugins` 面板中启用 **LiveLinkMasterLockit**（默认未启用）
2. 确保项目已启用 **Live Link** 插件
3. 通过 LiveLink 面板添加 MasterLockit 数据源
4. 使用 LiveLink 标准工作流将镜头数据应用到 CG 摄影机

### 最小 Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "LiveLink",
    "LiveLinkInterface"
});
```

## 模块依赖

### LiveLinkMasterLockit (Runtime)

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | LiveLink 框架接口（公开依赖） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Json` | 解析 MasterLockit 返回的 JSON 元数据 |
| `Networking` | 网络通信 |
| `Sockets` | TCP Socket 操作 |

### LiveLinkMasterLockitEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `LiveLinkMasterLockit` | 运行时模块 |
| `PropertyEditor` | 连接设置的 Details 面板 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-10-29 | `4fb04fde` | Add support for creating json objects from utf8 strings... | JSON 序列化基础设施更新，非本 plugin 的功能性改动 |
| 2024-01-25 | `f43fc1d7` | Fixed up more bool-taking calls to take EAllowShrinking instead | 编译适配：API 变更（bool → EAllowShrinking 枚举） |
| 2023-01-16 | `bbc37aa2` | Another batch iwyu updates to reduce number of includes | IWYU（Include What You Use）编译优化 |

### 维护评价

- **创建时间**: 2021-03-05，约 5 年前
- **最近更新**: 最近 3 次更新均为编译适配/基础设施变更，**无功能性更新**
- **IsBetaVersion=true, Installed=false**: 官方标记为 Beta，未默认安装
- **未实现功能**: 大量设备类型的 VolatileDataEvent 为 `Unimplemented`（Camera、SoundRecorder、TimecodeGenerator、SlateInfoDevice、Slate、Storage）
- **仅支持 Zeiss**: 镜头数据解析仅针对 `Carl Zeiss AG` 厂商
- **评价**: ⚠️ **实验性插件，功能不完整**。自 2021 年创建以来无实质性功能更新。如果你的片场不使用 Zeiss 镜头，此 plugin 无法工作。建议关注 Unreal 官方是否在新版本中完善此功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit)
- 官方文档（无，.uplugin 中 DocsURL 为空）
- [Ambient MasterLockit 官网](https://www.ambient.de/en/products/master-lockit/)（第三方硬件厂商）
