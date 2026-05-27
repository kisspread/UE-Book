# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照烘焙 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置 Actor） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPULightmass 是 Unreal Engine 传统 CPU 光照构建系统（Lightmass）的 **GPU 加速替代方案**，利用 **DXR（DirectX Raytracing）硬件加速光线追踪**来烘焙静态光照。

**解决的核心问题：**

传统 CPU Lightmass 的光照烘焙非常耗时，尤其在复杂场景中可能需要数十分钟甚至数小时。GPULightmass 通过 GPU 光线追踪将这一过程大幅加速，同时支持**交互式预览**——你可以在编辑器中实时看到光照烘焙的进展。

**核心功能：**

1. **Lightmap 路径追踪**：使用 DXR Ray Generation Shader 进行多弹射全局光照计算
2. **虚拟纹理瓦片系统**：将 Lightmap 分解为虚拟纹理瓦片，按需渲染可见区域
3. **辐照度缓存（Irradiance Caching）**：通过缓存间接光照采样来加速收敛并提升物理精度
4. **首次弹射光线引导（First Bounce Ray Guiding）**：智能寻找最亮方向分配采样权重
5. **体积光照图（Volumetric Lightmap）**：GPU 加速的 3D 体素化光照数据
6. **降噪**：集成 Intel OIDN 和简易萤火虫过滤器
7. **静态阴影深度图**：为静态光源烘焙阴影遮罩

**为什么存在：**

这是一个实验性功能，旨在探索用 GPU 硬件加速替代传统 CPU 光照烘焙的可行性。对于支持光线追踪硬件的 Windows 平台，它能提供显著更快的烘焙速度和交互式预览体验。

## 使用场景

- 你有一台支持 DXR 的 Windows 机器（RTX 显卡），想要**快速烘焙场景光照** → 启用 GPULightmass
- 你在做室内场景，想要**实时预览间接光照效果**调整材质和灯光 → 用 `Bake What You See` 模式
- 你的场景有复杂的间接光照，CPU Lightmass 烘焙太慢 → 切换到 GPU 光照烘焙
- 你需要在编辑器中**边移动相机边预览光照结果** → 启用 Realtime 模式

## 蓝图用法

### 核心节点

该插件通过 `UGPULightmassSubsystem`（World Subsystem）暴露蓝图 API。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Launch` | 启动光照烘焙 | `UGPULightmassSubsystem` |
| `Stop` | 停止光照烘焙 | `UGPULightmassSubsystem` |
| `IsRunning` | 查询烘焙是否正在进行 | `UGPULightmassSubsystem` |
| `GetPercentage` | 获取烘焙进度百分比 | `UGPULightmassSubsystem` |
| `GetSettings` | 获取光照设置对象 | `UGPULightmassSubsystem` |
| `SetRealtime` | 设置是否实时更新 | `UGPULightmassSubsystem` |
| `Save` | 保存烘焙结果 | `UGPULightmassSubsystem` |
| `StartRecordingVisibleTiles` | 开始录制可见瓦片 | `UGPULightmassSubsystem` |
| `EndRecordingVisibleTiles` | 结束录制可见瓦片 | `UGPULightmassSubsystem` |

### 设置参数（BlueprintReadWrite）

所有设置在 `UGPULightmassSettings` 上，可直接通过蓝图访问：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Mode` | `EGPULightmassMode` | FullBake | FullBake=全分辨率烘焙，BakeWhatYouSee=仅烘焙可见区域 |
| `GISamples` | `int32` | 512 | 每纹素的全局光照采样数（32-65536） |
| `StationaryLightShadowSamples` | `int32` | 128 | 静态阴影采样数 |
| `DenoisingOptions` | `EGPULightmassDenoisingOptions` | OnCompletion | 降噪时机：无/完成后/交互预览时 |
| `Den