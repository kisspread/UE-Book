# LiveLinkFreeD

> Live Link plugin for the FreeD protocol

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（需手动启用） |
| Beta 版本 | ⚠️ 是（IsBetaVersion = true） |
| 包含内容 | 是 |
| 模块 | LiveLinkFreeD (Runtime) |
| 支持程序 | 仅 LiveLinkHub |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5.2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkFreeD) | |

## 用途

LiveLinkFreeD 通过 UDP 接收 **FreeD 协议**的摄像机追踪数据，并将其桥接到 Unreal Engine 的 Live Link 系统。

FreeD（Free Dimensional）是广播行业广泛使用的摄像机追踪协议，由 Vinten Radamec 定义。该协议通过 UDP 发送 D1 类型数据包（29 字节），包含：

- **位置**（X/Y/Z）：17.6 定点数编码，单位 cm
- **旋转**（Yaw/Pitch/Roll）：8.15 定点数编码
- **焦距**（Focal Length）：24 位编码器值
- **对焦距离**（Focus Distance）：24 位编码器值
- **用户自定义数据**（通常为光圈 Iris）：16 位编码器值

插件在一个独立线程上监听 UDP 端口，解码 FreeD 数据包后通过 Live Link 推送 `FLiveLinkCameraFrameData`，使虚拟摄像机能够实时跟随物理摄像机运动。

**关键设计特点**：
- 编码器值支持**自动量程**（auto-ranging）和**手动量程**两种模式
- 内置 6 种摄像机厂商预设（Generic、Panasonic、Sony、Stype、Mosys、Ncam）
- X/Y 轴做了 FreeD→Unreal 的坐标系翻转
- 默认 subject 名称为 `Camera <CameraId>`，支持自定义覆盖

## 使用场景

- 你在做**虚拟制作（Virtual Production）**，需要将物理摄像机的追踪数据实时传输到 UE → 使用 LiveLinkFreeD 接收 FreeD 协议数据
- 你在使用 **LiveLinkHub** 管理多路 Live Link 数据源 → 此插件仅在 LiveLinkHub 中可用
- 你的摄像机追踪系统（如 Mosys、Ncam、Stype）输出 FreeD 协议 → 直接通过此插件接入
- 你需要将 FreeD 编码器数据（焦距/对焦/光圈）映射到虚拟摄像机属性 → 配置编码器参数即可

> ⚠️ **注意**：此插件默认禁用且为 Beta 状态，`SupportedPrograms` 限制为 `LiveLinkHub`。普通 UnrealEditor 项目中无法使用，需在 LiveLinkHub 环境中启用。

## 蓝图用法

此插件**没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。所有配置通过 Live Link 面板的 UI 完成，数据流完全在后台自动运行。

### UI 配置方式

通过 Live Link 面板添加 FreeD 源：

1. 打开 **Live Link** 面板（Window → Live Link）
2. 点击 **Source** 下拉菜单，选择 **LiveLinkFreeD Source**
3. 在弹出的子面板中配置连接参数：
   - **Local IP Address**：本地监听地址，`0.0.0.0` 表示绑定所有网络接口
   - **UDP Port Number**：监听端口，默认 `40000`
   - **Subject Name**：自定义主题名（留空则自动使用 `Camera <CameraId>`）
4. 点击 **Add** 创建源

### 源设置（Source Settings）

源创建后，可在 Live Link 面板中选中该源，修改以下设置：

| 设置 | 说明 |
|---|---|
| **Send Extra Meta Data** | 发送额外元数据（Camera ID 和 FrameCounter 字符串） |
| **Default Config** | 选择厂商预设（Generic / Panasonic / Sony / stYpe / Mosys / Ncam） |
| **Focus Distance Encoder Data** | 对焦距离编码器参数 |
| **Focal Length Encoder Data** | 焦距编码器参数 |
| **User Defined Encoder Data** | 用户自定义编码器参数（通常为光圈） |

每个编码器数据包含：

| 字段 | 说明 |
|---|---|
| **bIsValid** | 是否启用此编码器 |
| **bInvertEncoder** | 反转编码器输入方向 |
| **bUseManual Range** | 使用手动 Min/Max（默认为自动量程） |
| **Min** | 手动最小值（24 位范围） |
| **Max** | 手动最大值 |
| **MaskBits** | 原始编码器值的位掩码 |

### 厂商预设默认值

| 厂商 | 默认端口 | Zoom 范围 | Focus 范围 | Spare/UserDefined |
|---|---|---|---|---|
| Generic | 40000 | 0x0 – 0xFFFF | 0x0 – 0xFFFF | 未使用 |
| Panasonic | 1111 | 0x555 – 0xFFF | 0x555 – 0xFFF | Iris（反转） |
| Sony | 40000 | 0x0 – 0xFFFFFF | 0x7FFFFF – 0x000000 | 低 12 位 Iris |
| Mosys | 8001 | 0x0 – 0xFFFF | 0x0 – 0xFFFF | 未使用 |
| stYpe | 6301 | 0x0 – 0xFFFFFF | 0x0 – 0xFFFFFF | 未使用 |
| Ncam | 6301 | 0x0 – 0xFFFFFF | 0x0 – 0xFFFFFF | 未使用 |

## C++ 用法

此插件没有提供公开的 C++ API 扩展点。它是一个自包含的 Live Link Source 实现。如果需要在 C++ 中以编程方式创建 FreeD 源，可以通过 Live Link 的通用接口：

### 头文件引入

```cpp
#include "LiveLinkFreeDSource.h"
#include "LiveLinkFreeDConnectionSettings.h"
```

### 基本用法

通过连接设置创建 FreeD 源（参考 `LiveLinkFreeDSourceFactory.cpp`）：

```cpp
#include "LiveLinkFreeDSource.h"
#include "LiveLinkFreeDConnectionSettings.h"

// 配置连接参数
FLiveLinkFreeDConnectionSettings ConnectionSettings;
ConnectionSettings.IPAddress = TEXT("0.0.0.0");
ConnectionSettings.UDPPortNumber = 40000;
ConnectionSettings.SubjectName = TEXT(""); // 空 = 自动 "Camera <ID>"

// 创建源实例
TSharedPtr<FLiveLinkFreeDSource> Source = MakeShared<FLiveLinkFreeDSource>(ConnectionSettings);

// 通过 Live Link 系统注册（需要 ILiveLinkClient）
// 通常由 ULiveLinkFreeDSourceFactory 自动处理
```

> **来源**: `LiveLinkFreeDSourceFactory.cpp` 中的 `CreateSource()` 和 `CreateSourceFromSettings()` 方法。

### FreeD 协议解码

插件内部实现了 FreeD 协议的定点数解码：

```cpp
// 8.15 有符号定点数 → 浮点数（用于 Yaw/Pitch/Roll）
// 3 字节，高 8 位整数部分 + 低 15 位小数部分，除以 32768.0
float Decode_Signed_8_15(uint8* InBytes);

// 17.6 有符号定点数 → 浮点数（用于 X/Y/Z 位置，单位 cm）
// 3 字节，高 17 位整数部分 + 低 6 位小数部分，除以 640.0
float Decode_Signed_17_6(uint8* InBytes);

// 24 位无符号整数（用于焦距/对焦编码器原始值）
uint32 Decode_Unsigned_24(uint8* InBytes);

// 16 位无符号整数（用于用户自定义数据）
uint16 Decode_Unsigned_16(uint8* InBytes);

// 校验和：从 0x40 开始减去所有字节值
uint8 CalculateChecksum(uint8* InBytes, uint32 Size);
```

### 编码器数据处理

编码器原始值经过掩码、量程归一化和可选反转后输出 0.0–1.0 范围的浮点值：

```cpp
float FLiveLinkFreeDSource::ProcessEncoderData(FFreeDEncoderData& EncoderData, int32 RawEncoderValueInt)
{
    // 1. 应用位掩码
    RawEncoderValueInt &= EncoderData.MaskBits;

    // 2. 自动量程：跟踪历史 Min/Max
    if (!EncoderData.bUseManualRange) {
        if (RawEncoderValueInt < EncoderData.Min) EncoderData.Min = RawEncoderValueInt;
        if (RawEncoderValueInt > EncoderData.Max) EncoderData.Max = RawEncoderValueInt;
    }

    // 3. 归一化到 [0, 1]
    float FinalValue = (float)(RawEncoderValueInt - EncoderData.Min) / (float)(EncoderData.Max - EncoderData.Min);

    // 4. 可选反转
    if (EncoderData.bInvertEncoder) FinalValue = 1.0f - FinalValue;

    return FinalValue;
}
```

## 模块依赖

从 `LiveLinkFreeD.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Networking` | 网络功能 |
| `Sockets` | Socket 通信接口 |
| `LiveLinkInterface` | Live Link 框架接口 |
| `Messaging` | 消息传递系统 |
| `UdpMessaging` | UDP 消息传输（也是 Plugin 依赖） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `Slate` / `SlateCore` | UI 框架（用于配置面板，私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-10 | `f514a03` | Fix ip address tooltip | 修复 IP 地址输入框的提示文本 |
| 2025-08-10 | `8aebd22` | Add subject name override option | **功能更新**：新增自定义 Subject Name，不再强制使用 `Camera <ID>` |
| 2025-08-06 | `11d8ecb` | Clarified tooltip of ip address | 优化 IP 地址字段的 tooltip 说明 |

### 维护评价

- **年龄**：约 5.2 年，属于「老古董」级别
- **活跃度**：2025 年 8 月仍有实质性功能更新（Subject Name 覆盖），维护相对活跃
- **Beta 状态**：自 2021 年创建至今一直是 `IsBetaVersion = true`，未转正
- **受限部署**：仅支持 `LiveLinkHub`，不支持通用 UnrealEditor
- **代码规模**：11 个源文件，结构清晰，功能自包含
- **无测试用例**：未找到任何自动化测试
- **无官方文档链接**：`.uplugin` 中 DocsURL 为空

**综合评价**：此插件功能完整且持续维护，适合在 LiveLinkHub 环境中使用。但由于长期处于 Beta 状态且仅限 LiveLinkHub，不建议在通用项目中依赖它。如果你的 Virtual Production 工作流使用 LiveLinkHub 管理摄像机追踪数据，这是一个可靠的 FreeD 协议接入方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkFreeD)
- [FreeD 协议规范](https://www.manualsdir.com/manuals/641433/vinten-radamec-free-d.html)（源码中引用）
- 测试用例：无
