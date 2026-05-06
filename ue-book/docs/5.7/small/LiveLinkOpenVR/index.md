```markdown
# LiveLinkOpenVR

> Live Link plugin for OpenVR (Not supported for native arm64.)

| 属性 | 值 |
|---|---|
| 中文名 | OpenVR 实时链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOpenVR` (Runtime), `OpenVR` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR) | |

## 总体用途

LiveLinkOpenVR 将 **OpenVR（SteamVR）设备输入**（如手柄、头显）桥接到 Unreal Engine 的 **Live Link** 框架中。该插件专门为 **LiveLinkHub** 设计，允许用户在虚拟制片场景中直接使用 VR 手柄的按键、摇杆和姿态数据作为实时链接源。通过内置的角色映射，它可以将 SteamVR 的输入（按钮、触控板、扳机等）自动映射为 `LiveLinkGamepadInputDevice` 角色，从而与现有的游戏手柄输入管线无缝集成。

**解决什么问题？**  
在没有本机 VR 输入资源的场景（如虚拟制作、预可视化）中，需要将 VR 控制器的实时操作传递给引擎的 Live Link 系统，用于驱动虚拟相机、道具或角色绑定。LiveLinkOpenVR 提供了从物理 VR 设备到 Live Link 数据流的直接通道。

## 模块列表

| 模块 | 说明 | 文档链接 |
|---|---|---|
| `LiveLinkOpenVR` (Runtime) | 核心模块，包含 OpenVR 设备创建、帧同步、角色映射及 Live Link 源注册逻辑。 | [LiveLinkOpenVR.md](./LiveLinkOpenVR.md) |
| `OpenVR` (External) | 第三方 OpenVR SDK 包装，封装 SteamVR API 调用，提供跨平台接口（仅 Win64）。 | [OpenVR.md](./OpenVR.md) |

## 各模块一句话总结

- **LiveLinkOpenVR** – 实现 OpenVR 设备枚举、每帧数据采集、按键→LiveLinkGamepadInputDevice 映射，并将数据推送给 Live Link 客户端。
- **OpenVR** – 提供简化的 C++ 类型安全封装，负责初始化、帧循环、设备状态查询和 SHA-1 校验，底层依赖 SteamVR 运行时。

## 使用场景

- **虚拟制片 (Virtual Production)**：在摄影棚中使用 VR 手柄控制虚拟相机、灯光或角色，通过 Live Link 实时同步到虚幻引擎。
- **动作与姿态预览**：获取头显和手柄的 6-DoF 姿态数据，作为 Live Link 动画源，用于角色预绑定或跟踪系统测试。
- **混合输入方案**：将 SteamVR 扳机/触摸板输入与标准游戏手柄输入混合，通过 Live Link Hub 统一管理和路由。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR)
- [LiveLinkOpenVR 模块文档](./LiveLinkOpenVR.md)
- [OpenVR 第三方模块文档](./OpenVR.md)
```