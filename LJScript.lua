print("SET Impulse Version 1.0")
local mbWrite=MB.W
local mbRead=MB.R
local checkInterval=LJ.CheckInterval
local intervalConfig=LJ.IntervalConfig
local time_ms
local calibrate=1000
print("calibration ", calibrate)

--Time function
local function sleep(time_ms)
    intervalConfig(7, time_ms)
    while (checkInterval(7) ~= 1 ) do
    end
end
    
--Shuffle function
local function shuffle(list)
	for i = 6, 2, -1 do
		local j = math.random(i)
		list[i], list[j] = list[j], list[i]
	end
end

--Stimulation function
local function stim(amp)   --The pulse train
  for i=1, 5 do
    for j=1, 10 do
        mbWrite(30008,3, amp)
        sleep(0.04)
        mbWrite(30008,3, -amp)
        sleep(0.04)
    end
    mbWrite(30008,3, 0)
    sleep(17)  -- time between pulses
  end
end
  mbWrite(46010, 3, 1)
-- Main loop
LJ.Throttle = 500
while true do
 
  local rateStim = mbRead(46000, 3)/calibrate  -- RAM For Rating only
  local DTv = mbRead(46002, 3)/calibrate
  --print(DTv)
  local HTv = mbRead(46004, 3)/calibrate
  local HTTv = mbRead(46006, 3)/calibrate
  local IBI = 1000*60/(mbRead(0, 3)*84/5.0992)
  local currentValue
  local lastValue=0
  local iter=1
  local stimTable = {
      {0, DTv},
      {0, HTv},
      {0, HTTv},
      {0.2, DTv},
      {0.2, HTv},
      {0.2, HTTv},
  }
    
  if mbRead(46010, 3) == 1 then
    if rateStim ~= 0 then  --RATING
      stim(rateStim)
      print("rated ", rateStim)

    else  --stimulate
      if DTv ~= 0 then
        for i = 1, 11 do
          if mbRead(46008,3) ==1 then break end--Number fo table runs
          shuffle(stimTable) --shuffle table
          --for k,v in pairs(stimTable) do for k1,v1 in pairs(v) do print(k1,v1) end end
          while iter < 7 do
            if mbRead(46008,3) ==1 then break end
            --print(iter)--each table run
            currentValue = mbRead(2006, 1)  --read trigger
            print(currentValue,"currentValue", lastValue, "lastValue", iter)
              if currentValue > 0 then  --STIMULATION if there is a rising pulse
                sleep(IBI*stimTable[iter][1]+0.01)
                stim(stimTable[iter][2])
                print("stimulating", stimTable[iter][2])
                  if mbRead(46008,3) ==1 then break end
                  
                --print(stimTable[j]["amp"], "  ", stimTable[j]["delay"])
                sleep(5000) --wait between rows
              else
                --lastValue = currentValue
                iter=iter-1
                sleep(10)  --wait for trigger to change
              end
              iter=iter+1
          end
          sleep(15000)  --delay between tables
          iter=1
        end
    end
   
    end
   mbWrite(46010, 3, 0)
    print("yes")
    
    sleep(1000)
  end
end