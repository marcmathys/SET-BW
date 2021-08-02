local function stim(amp)   --The pulse train
    for i=1, 5 do
         for j=1, 10 do
             --mbWrite(1000,3, amp)
             mbWrite(1000,3, 2.5 + amp)
             sleep(0.41)
             --mbWrite(1000,3, 0) 
             --mbWrite(1002,3, amp)  --low
             mbWrite(1000,3, 2.5 - amp)
             sleep(0.41)
             --mbWrite(1002,3, 0)
         end
         mbWrite(1000,3, 2.5)
         sleep(17)  -- time between pulses
    end
  end