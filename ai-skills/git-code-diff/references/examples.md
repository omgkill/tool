# 代码参数对比示例

## 示例1：DispatchSendReward 发奖励函数改造

### 改造概述

**改造内容**：将多个分散的发奖励函数统一为 DispatchSendReward

**改造前函数**：
- sendVip()
- sendSingleReward()
- sendSingleRewardPoolAndVip()
- sendRewardWithManual()

**改造后函数**：
- DispatchSendReward()

### 完整参数对比

#### Shake（摇晃）场景

**改造前**：
```go
// 入口调用
manualRes, sErr := s.sendSingleRewardPoolAndVipWithManual(ctx, openID, vipTid, 
    risk.RiskPlayIDType_Shake, t, rsp.Pool)

// 手动记录
s.svc.Go(func(svc types.Service) {
    _ = s.lPushRecord(openID, api.RecordType_RecordType_Shake, t, tid, rsp.Pool)
})
```

| 参数 | 值 | 来源 |
|-----|-----|------|
| openID | openID | 直接使用 |
| tid | vipTid | util.TransactionId(tid) |
| playID | risk.RiskPlayIDType_Shake | 常量 |
| nowT | t | 当前时间 |
| pool | rsp.Pool | 奖池结果 |

**改造后**：
```go
rsp.GetInfo, err = s.DispatchSendReward(ctx, openID, vipTid, 
    risk.RiskPlayIDType_Shake, t, rsp.Pool, 
    api.RecordType_RecordType_Shake, WithCheckVip())
```

| 参数 | 值 | 对比结果 |
|-----|-----|---------|
| openID | openID | ✅ 一致 |
| tid | vipTid | ✅ 一致 |
| riskType | risk.RiskPlayIDType_Shake | ✅ 一致 |
| nowT | t | ✅ 一致 |
| input | rsp.Pool | ✅ 一致 |
| recordType | api.RecordType_RecordType_Shake | ✅ 新增参数 |
| options | WithCheckVip() | ✅ 新增参数 |

---

#### ShakeAward（摇晃广告后置领奖）场景

**改造前**：
```go
// 入口调用
manualRes, sErr := s.sendSingleRewardPoolAndVipWithManual(ctx, openID, tid, 
    risk.RiskPlayIDType_Shake, nowT, rp)

// 广告后置记录
s.svc.Go(func(svc types.Service) {
    _ = s.lPushAdAfter(openID, api.RecordType_RecordType_Shake, nowT, req.GetLastTid(), rp)
})
```

**改造后**：
```go
rspReward, err = s.DispatchSendReward(ctx, openID, tid, 
    risk.RiskPlayIDType_Shake, nowT, rp, 
    api.RecordType_RecordType_Shake, 
    WithCheckVip(), WithUseAdAfter(req.GetLastTid()))
```

| 参数 | 值 | 对比结果 |
|-----|-----|---------|
| openID | openID | ✅ 一致 |
| tid | tid | ✅ 一致 |
| riskType | risk.RiskPlayIDType_Shake | ✅ 一致 |
| nowT | nowT | ✅ 一致 |
| input | rp | ✅ 一致 |
| recordType | api.RecordType_RecordType_Shake | ✅ 新增 |
| options | WithCheckVip(), WithUseAdAfter(req.GetLastTid()) | ⚠️ 需确认 req.GetLastTid() |

**⚠️ 需确认点**：
- 改造前 lPushAdAfter 最后一个参数是 rp（奖池）
- 改造后 WithUseAdAfter(req.GetLastTid()) 只传了 lastTid
- 需要确认 lastTid 的用途是否正确

---

#### ShareRankAward（分享排行奖励）场景

**改造前**：
```go
manualRes, sErr := s.sendSingleRewardWithManual(ctx, openID, shareUserRank.RankTid, 
    risk.RiskPlayIDType_ShareRankAward, nowT, 
    &reward_sender.Reward{
        RewardId: rewardSimple.RewardId,
        Num:      int64(rewardSimple.RewardCount),
    })

// 手动记录
s.svc.Go(func(svc types.Service) {
    _ = s.lPushRecord(openID, api.RecordType_RecordType_Share_Rank, nowT, 
        shareUserRank.RankTid, &comm.RewardPool{
            RewardId:    rewardSimple.RewardId,
            RewardCount: rewardSimple.RewardCount,
        })
})
```

**改造后**：
```go
rspReward, err = s.DispatchSendReward(ctx, openID, shareUserRank.RankTid, 
    risk.RiskPlayIDType_ShareRankAward, nowT, 
    rewardSimple,  // 直接传 comm.RewardSimple
    api.RecordType_RecordType_Share_Rank)
```

| 参数 | 值 | 对比结果 |
|-----|-----|---------|
| openID | openID | ✅ 一致 |
| tid | shareUserRank.RankTid | ✅ 一致 |
| riskType | risk.RiskPlayIDType_ShareRankAward | ✅ 一致 |
| nowT | nowT | ✅ 一致 |
| input | rewardSimple | ✅ 简化了类型 |
| recordType | api.RecordType_RecordType_Share_Rank | ✅ 新增 |
| options | 无 | ✅ 合理，无VIP检查 |

---

## 示例2：邮件相关参数对比

### MailData 结构体字段变化

**改造前**：
```go
type MailData struct {
    MailID      string               `json:"mid"`
    RewardList  []*comm.RewardSimple `json:"rl"`
    RewardScene string               `json:"rs"`      // string 类型
    PlayID      string               `json:"pid"`      // 旧字段
    CreateTime int64                `json:"ct"`
    ExpireTime int64                `json:"et"`       // 旧字段
    RewardTid  string               `json:"rtid"`     // 旧字段
}
```

**改造后**：
```go
type MailData struct {
    MailID         string               `json:"mid"`
    RewardList     []*comm.RewardSimple `json:"rl"`
    RewardScene    int32                `json:"rs"`       // int32 类型
    RiskPlayIdType string               `json:"rt"`       // 新字段名
    CreateTime     int64                `json:"ct"`
    UseAdAfter     bool                 `json:"ua"`       // 新字段
}
```

| 字段 | 改造前 | 改造后 | 评估 |
|------|--------|--------|------|
| MailID | UUID | params.tid | ⚠️ |
| RewardScene | string | int32 | ✅ |
| PlayID | string | - | ❌ 已删除 |
| RiskPlayIdType | - | string | ✅ |
| CreateTime | int64 | int64 | ✅ |
| ExpireTime | int64 | - | ❌ 已删除，改用计算 |
| UseAdAfter | - | bool | ✅ |

---

## 问题汇总表

| # | 场景 | 问题描述 | 严重程度 | 建议 |
|---|------|----------|----------|------|
| 1 | MailID 生成 | 从 UUID 改为使用 tid | ⚠️ 中 | 需确认是否会重复 |
| 2 | ExpireTime | 从存储改为计算 | ✅ | 无问题 |
| 3 | ShakeAward | lastTid 传递方式变化 | ⚠️ 低 | 需确认业务逻辑 |
| 4 | PlayID 字段 | 已删除 | ✅ | 字段已废弃 |

---

## 验证清单

### DispatchSendReward 改造验证

- 所有业务场景都已迁移到新函数
- 参数顺序和类型完全一致
- 新增的 recordType 参数正确
- options 中的函数调用参数正确
- 返回值正确处理

### MailData 改造验证

- MailID 生成逻辑正确
- ExpireTime 计算逻辑正确
- RiskPlayIdType 赋值正确
- UseAdAfter 使用正确

### 风控改造验证

- 所有调用处正确接收新返回值
- 错误处理逻辑正确
- 风控状态判断逻辑正确
